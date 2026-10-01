/**
 * MemoChampi - Moteur de jeu interactif & Quiz mycologique
 * HTML5 / CSS3 / JavaScript Vanilla
 */

(function () {
    'use strict';

    // --- État de l'application ---
    const AppState = {
        mode: 'all',                // 'all', 'edible', 'toxic', 'famous'
        questionCount: 20,          // Par défaut 20 propositions
        showClues: true,            // Affiche la famille comme indice
        currentIndex: 0,
        score: 0,
        questions: [],              // Liste des questions générées
        isAnswered: false,
        autoAdvanceTimer: null,
        startTime: null,
        endTime: null,
        lightboxActive: false
    };

    // --- Sélecteurs DOM ---
    const DOM = {
        // Thème & Son
        themeToggle: document.getElementById('btn-toggle-theme'),
        soundToggle: document.getElementById('btn-toggle-sound'),
        btnOpenMycoNav: document.getElementById('btn-open-mycotheque'),
        brandLogo: document.getElementById('brand-logo'),

        // Écrans
        screenSetup: document.getElementById('screen-setup'),
        screenQuiz: document.getElementById('screen-quiz'),
        screenBilan: document.getElementById('screen-bilan'),

        // Setup
        selectMode: document.getElementById('select-mode'),
        selectCount: document.getElementById('select-count'),
        checkClues: document.getElementById('check-clues'),
        btnStartQuiz: document.getElementById('btn-start-quiz'),
        btnOpenMycoSetup: document.getElementById('btn-open-mycotheque-setup'),
        statGamesPlayed: document.getElementById('stat-games-played'),
        statBestScore: document.getElementById('stat-best-score'),
        statSuccessRate: document.getElementById('stat-success-rate'),

        // Quiz Header & Progress
        quizProgressText: document.getElementById('quiz-progress-text'),
        quizScoreLive: document.getElementById('quiz-score-live'),
        quizProgressBar: document.getElementById('quiz-progress-bar'),

        // Quiz Stage (Image)
        mushroomImg: document.getElementById('mushroom-img'),
        imgSkeleton: document.getElementById('img-skeleton'),
        clueFamilyTag: document.getElementById('clue-family-tag'),
        btnZoomImg: document.getElementById('btn-zoom-img'),

        // Quiz Questions & Options
        optionsContainer: document.getElementById('options-container'),
        eduCard: document.getElementById('educational-card'),
        eduCommonName: document.getElementById('edu-common-name'),
        eduLatinName: document.getElementById('edu-latin-name'),
        eduBadge: document.getElementById('edu-badge'),
        eduWarning: document.getElementById('edu-warning'),
        eduCap: document.getElementById('edu-cap'),
        eduUnderside: document.getElementById('edu-underside'),
        eduStem: document.getElementById('edu-stem'),
        eduHabitat: document.getElementById('edu-habitat'),
        eduSeason: document.getElementById('edu-season'),
        eduConfusion: document.getElementById('edu-confusion'),
        eduFunfactText: document.getElementById('edu-funfact-text'),
        btnNextQuestion: document.getElementById('btn-next-question'),

        // Bilan
        bilanScoreRaw: document.getElementById('bilan-score-raw'),
        bilanScorePercent: document.getElementById('bilan-score-percent'),
        bilanTime: document.getElementById('bilan-time'),
        bilanRankBadge: document.getElementById('bilan-rank-badge'),
        bilanRankComment: document.getElementById('bilan-rank-comment'),
        bilanReviewList: document.getElementById('bilan-review-list'),
        btnRestartQuiz: document.getElementById('btn-restart-quiz'),
        btnBilanToSetup: document.getElementById('btn-bilan-to-setup'),
        btnOpenMycoBilan: document.getElementById('btn-open-mycotheque-bilan'),

        // Modals
        modalMycotheque: document.getElementById('modal-mycotheque'),
        btnCloseMyco: document.getElementById('btn-close-mycotheque'),
        mycoSearch: document.getElementById('myco-search'),
        mycoFilter: document.getElementById('myco-filter'),
        mycoGrid: document.getElementById('myco-grid'),

        modalDetail: document.getElementById('modal-detail'),
        btnCloseDetail: document.getElementById('btn-close-detail'),
        detailContent: document.getElementById('detail-modal-content'),

        lightboxBackdrop: document.getElementById('lightbox-backdrop'),
        lightboxImg: document.getElementById('lightbox-img'),
        lightboxCaption: document.getElementById('lightbox-caption'),
        btnCloseLightbox: document.getElementById('btn-close-lightbox')
    };

    // =========================================================================
    // Initialisation
    // =========================================================================

    function init() {
        initTheme();
        initSound();
        loadLocalStats();
        bindEvents();
        preloadImages();
    }

    // Gestion du thème Sombre / Clair
    function initTheme() {
        const savedTheme = localStorage.getItem('memochampi_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('memochampi_theme', nextTheme);
        updateThemeIcon(nextTheme);
        SoundEngine.playClick();
    }

    function updateThemeIcon(theme) {
        if (DOM.themeToggle) {
            DOM.themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
            DOM.themeToggle.title = theme === 'dark' ? 'Passer en thème clair' : 'Passer en thème sombre';
        }
    }

    // Gestion du son
    function initSound() {
        const isMuted = SoundEngine.loadMuteState();
        updateSoundIcon(isMuted);
    }

    function toggleSound() {
        const isMuted = SoundEngine.toggleMute();
        updateSoundIcon(isMuted);
        if (!isMuted) SoundEngine.playClick();
    }

    function updateSoundIcon(isMuted) {
        if (DOM.soundToggle) {
            DOM.soundToggle.textContent = isMuted ? '🔇' : '🔊';
            DOM.soundToggle.title = isMuted ? 'Activer le son' : 'Couper le son';
        }
    }

    // Préchargement discret des images en tâche de fond
    function preloadImages() {
        if (typeof MUSHROOMS !== 'undefined' && Array.isArray(MUSHROOMS)) {
            MUSHROOMS.slice(0, 15).forEach(m => {
                const img = new Image();
                img.src = m.image;
            });
        }
    }

    // =========================================================================
    // Statistiques Locales
    // =========================================================================

    function loadLocalStats() {
        const played = parseInt(localStorage.getItem('memochampi_games') || '0', 10);
        const best = parseInt(localStorage.getItem('memochampi_best') || '0', 10);
        const totalCorrect = parseInt(localStorage.getItem('memochampi_tot_correct') || '0', 10);
        const totalQuestions = parseInt(localStorage.getItem('memochampi_tot_q') || '0', 10);

        if (DOM.statGamesPlayed) DOM.statGamesPlayed.textContent = played;
        if (DOM.statBestScore) DOM.statBestScore.textContent = `${best} / 20`;

        const rate = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
        if (DOM.statSuccessRate) DOM.statSuccessRate.textContent = `${rate}%`;
    }

    function saveGameStats(score, totalCount, durationSeconds) {
        const played = parseInt(localStorage.getItem('memochampi_games') || '0', 10) + 1;
        const currentBest = parseInt(localStorage.getItem('memochampi_best') || '0', 10);
        const normalizedScore = Math.round((score / totalCount) * 20);
        const newBest = Math.max(currentBest, normalizedScore);

        const totalCorrect = parseInt(localStorage.getItem('memochampi_tot_correct') || '0', 10) + score;
        const totalQuestions = parseInt(localStorage.getItem('memochampi_tot_q') || '0', 10) + totalCount;

        localStorage.setItem('memochampi_games', played);
        localStorage.setItem('memochampi_best', newBest);
        localStorage.setItem('memochampi_tot_correct', totalCorrect);
        localStorage.setItem('memochampi_tot_q', totalQuestions);

        loadLocalStats();
    }

    // =========================================================================
    // Moteur de Quiz & Génération des Questions
    // =========================================================================

    function startQuiz() {
        SoundEngine.playClick();

        AppState.mode = DOM.selectMode.value;
        AppState.questionCount = parseInt(DOM.selectCount.value, 10) || 20;
        AppState.showClues = DOM.checkClues.checked;
        AppState.score = 0;
        AppState.currentIndex = 0;
        AppState.startTime = Date.now();
        AppState.endTime = null;

        // Filtrer le pool de champignons selon le mode
        let pool = filterMushroomPool(AppState.mode);
        if (pool.length < 4) {
            pool = [...MUSHROOMS];
        }

        // Mélanger le pool
        pool = shuffleArray(pool);

        // Sélectionner les cibles
        const targets = [];
        let poolIndex = 0;
        while (targets.length < AppState.questionCount) {
            targets.push(pool[poolIndex % pool.length]);
            poolIndex++;
        }

        // Générer les 4 options pour chaque cible
        AppState.questions = targets.map(target => {
            const distractors = generateDistractors(target, MUSHROOMS);
            const options = shuffleArray([target, ...distractors]);
            return {
                target: target,
                options: options,
                userAnswer: null,
                isCorrect: null
            };
        });

        // Afficher l'écran de Quiz
        showScreen('quiz');
        renderQuestion(AppState.currentIndex);
    }

    function filterMushroomPool(mode) {
        if (!window.MUSHROOMS || !Array.isArray(window.MUSHROOMS)) return [];

        switch (mode) {
            case 'edible':
                return MUSHROOMS.filter(m => m.category === 'edible_choice' || m.category === 'edible');
            case 'toxic':
                return MUSHROOMS.filter(m => m.category === 'toxic' || m.category === 'deadly');
            case 'famous':
                // Les espèces les plus emblématiques des sous-bois
                return MUSHROOMS.filter(m =>
                    ['cepe_de_bordeaux', 'girolle', 'trompette_de_la_mort', 'morille_commune',
                     'coulemelle', 'pied_de_mouton', 'oronge', 'lactaire_delicieux',
                     'pleurote_en_huitre', 'agaric_champetre', 'coprin_chevelu', 'amanite_phalloide',
                     'amanite_tue_mouches', 'amanite_panthere', 'bolet_de_satan', 'gyromitre',
                     'sparassis_crepu', 'langue_de_boeuf', 'clathre_rouge', 'vesse_de_loup_geante',
                     'truffe_noire', 'hydne_herisson', 'bolet_a_pied_rouge', 'laccaire_amethyste',
                     'tricholome_de_la_saint_georges', 'flammuline_a_pied_veloute'].includes(m.id)
                );
            default:
                return [...MUSHROOMS];
        }
    }

    /**
     * Générateur de distracteurs intelligents :
     * Sélectionne prioritairement des champignons de la même famille,
     * ou des confusions fréquentes documentées.
     */
    function generateDistractors(target, allMushrooms) {
        const distractors = [];
        const candidates = allMushrooms.filter(m => m.id !== target.id);

        // 1. Chercher dans la même famille
        const sameFamily = candidates.filter(m => m.family === target.family);
        if (sameFamily.length > 0) {
            const picked = shuffleArray(sameFamily)[0];
            distractors.push(picked);
        }

        // 2. Chercher dans la même catégorie de toxicité / comestibilité
        const sameCategory = candidates.filter(m =>
            m.category === target.category && !distractors.some(d => d.id === m.id)
        );
        if (sameCategory.length > 0) {
            const picked = shuffleArray(sameCategory)[0];
            distractors.push(picked);
        }

        // 3. Compléter avec d'autres champignons aléatoires jusqu'à en avoir 3
        const remaining = candidates.filter(m => !distractors.some(d => d.id === m.id));
        const shuffledRemaining = shuffleArray(remaining);

        while (distractors.length < 3 && shuffledRemaining.length > 0) {
            distractors.push(shuffledRemaining.pop());
        }

        return distractors;
    }

    // =========================================================================
    // Affichage de la Question courante
    // =========================================================================

    function renderQuestion(index) {
        clearTimeout(AppState.autoAdvanceTimer);
        AppState.isAnswered = false;

        const q = AppState.questions[index];
        const target = q.target;

        // Mise à jour de l'en-tête
        DOM.quizProgressText.textContent = `Question ${index + 1} / ${AppState.questionCount}`;
        DOM.quizScoreLive.textContent = `Score : ${AppState.score}`;
        const percent = ((index) / AppState.questionCount) * 100;
        DOM.quizProgressBar.style.width = `${percent}%`;

        // Indice de famille
        if (AppState.showClues && target.family) {
            DOM.clueFamilyTag.textContent = `Famille : ${target.family}`;
            DOM.clueFamilyTag.parentElement.classList.remove('hidden');
        } else {
            DOM.clueFamilyTag.parentElement.classList.add('hidden');
        }

        // Chargement de l'image avec skeleton loader
        DOM.imgSkeleton.classList.remove('hidden');
        DOM.mushroomImg.classList.add('hidden');

        const imgObj = new Image();
        imgObj.src = target.image;
        imgObj.onload = () => {
            DOM.mushroomImg.src = target.image;
            DOM.mushroomImg.alt = `Champignon mystère n°${index + 1}`;
            DOM.imgSkeleton.classList.add('hidden');
            DOM.mushroomImg.classList.remove('hidden');
        };
        imgObj.onerror = () => {
            // Fallback sur l'URL distante si l'image locale échoue
            DOM.mushroomImg.src = target.remoteImage || target.image;
            DOM.imgSkeleton.classList.add('hidden');
            DOM.mushroomImg.classList.remove('hidden');
        };

        // Construction des 4 boutons d'options
        DOM.optionsContainer.innerHTML = '';
        const keys = ['1', '2', '3', '4'];

        q.options.forEach((opt, idx) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.dataset.id = opt.id;
            btn.dataset.key = keys[idx];

            btn.innerHTML = `
                <span class="opt-badge-key">${keys[idx]}</span>
                <div class="opt-text-wrap">
                    <span class="opt-common-name">${opt.name}</span>
                    <span class="opt-latin-name">${opt.latin}</span>
                </div>
            `;

            btn.addEventListener('click', () => handleOptionSelect(opt, btn));
            DOM.optionsContainer.appendChild(btn);
        });

        // Masquer la fiche éducative et le bouton suivant
        DOM.eduCard.classList.add('hidden');
        DOM.btnNextQuestion.classList.add('hidden');
    }

    // =========================================================================
    // Gestion de la sélection d'une réponse
    // =========================================================================

    function handleOptionSelect(selectedMushroom, selectedBtn) {
        if (AppState.isAnswered) return;
        AppState.isAnswered = true;

        const currentQ = AppState.questions[AppState.currentIndex];
        const isCorrect = (selectedMushroom.id === currentQ.target.id);

        currentQ.userAnswer = selectedMushroom;
        currentQ.isCorrect = isCorrect;

        // Désactiver tous les boutons d'options
        const allButtons = DOM.optionsContainer.querySelectorAll('.option-btn');
        allButtons.forEach(btn => {
            btn.disabled = true;
            if (btn.dataset.id === currentQ.target.id) {
                btn.classList.add('correct');
            }
        });

        if (isCorrect) {
            AppState.score++;
            SoundEngine.playCorrect();
            selectedBtn.classList.add('correct');
        } else {
            SoundEngine.playWrong();
            selectedBtn.classList.add('wrong');
        }

        // Mettre à jour le score live
        DOM.quizScoreLive.textContent = `Score : ${AppState.score}`;

        // Remplir et afficher la Fiche Mycologique
        populateEducationalCard(currentQ.target);
        DOM.eduCard.classList.remove('hidden');
        DOM.btnNextQuestion.classList.remove('hidden');
    }

    function populateEducationalCard(m) {
        DOM.eduCommonName.textContent = m.name;
        DOM.eduLatinName.textContent = m.latin;

        // Badge comestibilité
        DOM.eduBadge.className = `badge-edibility ${m.edibility || 'sans_interet'}`;
        DOM.eduBadge.textContent = m.edibilityLabel || 'Non documenté';

        // Alerte avertissement
        if (m.warning) {
            DOM.eduWarning.textContent = m.warning;
            DOM.eduWarning.classList.remove('hidden');
        } else {
            DOM.eduWarning.classList.add('hidden');
        }

        // Grille de caractéristiques
        DOM.eduCap.textContent = m.cap || '—';
        DOM.eduUnderside.textContent = m.underside || '—';
        DOM.eduStem.textContent = m.stem || '—';
        DOM.eduHabitat.textContent = m.habitat || '—';
        DOM.eduSeason.textContent = m.season || '—';
        DOM.eduConfusion.textContent = m.confusion || '—';
        DOM.eduFunfactText.textContent = m.funFact || '—';
    }

    function nextQuestion() {
        clearTimeout(AppState.autoAdvanceTimer);
        SoundEngine.playClick();

        if (AppState.currentIndex < AppState.questionCount - 1) {
            AppState.currentIndex++;
            renderQuestion(AppState.currentIndex);
        } else {
            finishQuiz();
        }
    }

    // =========================================================================
    // Écran de Bilan & Fin de Partie
    // =========================================================================

    function finishQuiz() {
        AppState.endTime = Date.now();
        const durationSec = Math.round((AppState.endTime - AppState.startTime) / 1000);
        const minutes = Math.floor(durationSec / 60);
        const seconds = durationSec % 60;
        const timeFormatted = `${minutes > 0 ? minutes + ' min ' : ''}${seconds} s`;

        // Calcul note normalisée sur 20
        const noteSur20 = Math.round((AppState.score / AppState.questionCount) * 20);
        const percent = Math.round((AppState.score / AppState.questionCount) * 100);

        // Sauvegarder les statistiques
        saveGameStats(AppState.score, AppState.questionCount, durationSec);

        // Affichage des métriques
        DOM.bilanScoreRaw.textContent = `${AppState.score} / ${AppState.questionCount}`;
        DOM.bilanScorePercent.textContent = `${noteSur20} / 20 (${percent}%)`;
        DOM.bilanTime.textContent = timeFormatted;

        // Rang mycologique
        let rankClass = 'rank-novice';
        let rankBadge = '';
        let rankComment = '';

        if (noteSur20 >= 20) {
            rankClass = 'rank-perfect';
            rankBadge = '🏆 Grand Maître Mycologue';
            rankComment = 'Score absolu parfait ! Vous distinguez les espèces les plus délicates les yeux fermés. Vous êtes prêt pour la cueillette en toute sécurité !';
            SoundEngine.playFanfare();
        } else if (noteSur20 >= 17) {
            rankClass = 'rank-expert';
            rankBadge = '🌲 Cueilleur Expert';
            rankComment = 'Chapeau bas ! Votre panier est toujours bien rempli et vos connaissances sur les caractéristiques distinctives sont remarquables.';
            SoundEngine.playFanfare();
        } else if (noteSur20 >= 13) {
            rankClass = 'rank-intermediate';
            rankBadge = '🍄 Amateur Averti';
            rankComment = 'Très beau résultat ! Vous connaissez les fondamentaux. Veillez simplement à bien mémoriser les confusions à risque.';
            SoundEngine.playCorrect();
        } else if (noteSur20 >= 8) {
            rankClass = 'rank-intermediate';
            rankBadge = '🍃 Cueilleur Débutant';
            rankComment = 'Des bases intéressantes, mais restez prudent en forêt ! Ne consommez jamais un spécimen en cas de doute persistant.';
            SoundEngine.playCorrect();
        } else {
            rankClass = 'rank-novice';
            rankBadge = '⚠️ Novice des Sous-Bois';
            rankComment = 'Prudence absolue ! Vous avez encore besoin d\'entraînement pour ne pas risquer l\'intoxication. Consultez notre Mycothèque pour réviser !';
            SoundEngine.playWrong();
        }

        DOM.bilanRankBadge.className = `rank-badge ${rankClass}`;
        DOM.bilanRankBadge.textContent = rankBadge;
        DOM.bilanRankComment.textContent = rankComment;

        // Générer le tableau récapitulatif des 20 propositions
        DOM.bilanReviewList.innerHTML = '';
        AppState.questions.forEach((q, idx) => {
            const item = document.createElement('div');
            item.className = `review-item ${q.isCorrect ? 'is-correct' : 'is-wrong'}`;

            const badgeEdib = `<span class="badge-edibility ${q.target.edibility}" style="font-size: 0.72rem; padding: 0.2rem 0.5rem;">${q.target.edibilityLabel.split(' ')[0]} ${q.target.edibilityLabel.split(' ')[1] || ''}</span>`;

            let userText = '';
            if (q.isCorrect) {
                userText = `<span class="review-user-ans correct">✅ Réponse correcte : ${q.target.name}</span>`;
            } else {
                userText = `<span class="review-user-ans wrong">❌ Vous aviez choisi : <strong>${q.userAnswer ? q.userAnswer.name : 'Aucune'}</strong></span>`;
            }

            item.innerHTML = `
                <img class="review-thumb" src="${q.target.image}" alt="${q.target.name}" onerror="this.src='${q.target.remoteImage}';">
                <div class="review-details">
                    <div class="review-name">
                        <span>#${idx + 1} ${q.target.name}</span>
                        ${badgeEdib}
                    </div>
                    ${userText}
                </div>
                <div class="review-actions">
                    <button class="btn-review-sheet" title="Voir la fiche complète">🔍 Fiche</button>
                </div>
            `;

            item.querySelector('.btn-review-sheet').addEventListener('click', () => {
                openDetailModal(q.target);
            });

            DOM.bilanReviewList.appendChild(item);
        });

        // Afficher l'écran de bilan
        showScreen('bilan');
    }

    // =========================================================================
    // Navigation entre les Écrans
    // =========================================================================

    function showScreen(name) {
        DOM.screenSetup.classList.add('hidden');
        DOM.screenQuiz.classList.add('hidden');
        DOM.screenBilan.classList.add('hidden');

        if (name === 'setup') {
            DOM.screenSetup.classList.remove('hidden');
        } else if (name === 'quiz') {
            DOM.screenQuiz.classList.remove('hidden');
        } else if (name === 'bilan') {
            DOM.screenBilan.classList.remove('hidden');
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // =========================================================================
    // Mycothèque (Encyclopédie interactive complète)
    // =========================================================================

    function openMycothequeModal() {
        SoundEngine.playClick();
        DOM.modalMycotheque.classList.remove('hidden');
        DOM.mycoSearch.value = '';
        DOM.mycoFilter.value = 'all';
        renderMycothequeGrid();
    }

    function closeMycothequeModal() {
        DOM.modalMycotheque.classList.add('hidden');
    }

    function renderMycothequeGrid() {
        if (!window.MUSHROOMS) return;

        const query = DOM.mycoSearch.value.trim().toLowerCase();
        const filterCategory = DOM.mycoFilter.value;

        const filtered = MUSHROOMS.filter(m => {
            const matchesText = m.name.toLowerCase().includes(query) ||
                                m.latin.toLowerCase().includes(query) ||
                                m.family.toLowerCase().includes(query);

            let matchesCat = true;
            if (filterCategory === 'excellent') {
                matchesCat = (m.edibility === 'excellent');
            } else if (filterCategory === 'comestible') {
                matchesCat = (m.edibility === 'comestible' || m.edibility === 'excellent');
            } else if (filterCategory === 'toxic') {
                matchesCat = (m.edibility === 'toxique');
            } else if (filterCategory === 'deadly') {
                matchesCat = (m.edibility === 'mortel');
            } else if (filterCategory === 'inedible') {
                matchesCat = (m.edibility === 'sans_interet');
            }

            return matchesText && matchesCat;
        });

        DOM.mycoGrid.innerHTML = '';
        if (filtered.length === 0) {
            DOM.mycoGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem;">Aucun champignon ne correspond à votre recherche.</p>';
            return;
        }

        filtered.forEach(m => {
            const card = document.createElement('div');
            card.className = 'myco-card';
            card.innerHTML = `
                <img class="myco-card-img" src="${m.image}" alt="${m.name}" loading="lazy" onerror="this.src='${m.remoteImage}';">
                <div class="myco-card-info">
                    <span class="myco-card-title">${m.name}</span>
                    <span class="myco-card-latin">${m.latin}</span>
                    <span class="badge-edibility ${m.edibility}" style="font-size: 0.72rem; padding: 0.2rem 0.5rem; align-self: flex-start;">
                        ${m.edibilityLabel}
                    </span>
                </div>
            `;
            card.addEventListener('click', () => {
                openDetailModal(m);
            });
            DOM.mycoGrid.appendChild(card);
        });
    }

    // Modal Fiche Détaillée
    function openDetailModal(m) {
        SoundEngine.playClick();

        DOM.detailContent.innerHTML = `
            <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
                <img src="${m.image}" alt="${m.name}" style="width: 260px; height: 200px; object-fit: cover; border-radius: var(--radius-md); box-shadow: 0 4px 12px rgba(0,0,0,0.3);" onerror="this.src='${m.remoteImage}';">
                <div style="flex: 1; min-width: 240px;">
                    <h3 style="font-size: 1.4rem; font-weight: 800; margin-bottom: 0.25rem;">${m.name}</h3>
                    <p style="font-style: italic; color: var(--text-muted); margin-bottom: 0.75rem;">${m.latin} — Famille : ${m.family}</p>
                    <span class="badge-edibility ${m.edibility}" style="font-size: 0.85rem; padding: 0.35rem 0.85rem; margin-bottom: 0.75rem; display: inline-flex;">
                        ${m.edibilityLabel}
                    </span>
                    ${m.warning ? `<p style="color: var(--wrong-text); background: rgba(239, 68, 68, 0.15); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.88rem; font-weight: 600; margin-top: 0.5rem;">${m.warning}</p>` : ''}
                </div>
            </div>

            <div class="edu-info-grid" style="font-size: 0.92rem; gap: 1rem 1.5rem;">
                <div class="edu-item"><strong>Chapeau</strong><span>${m.cap || '—'}</span></div>
                <div class="edu-item"><strong>Dessous (Tubes/Lames)</strong><span>${m.underside || '—'}</span></div>
                <div class="edu-item"><strong>Pied</strong><span>${m.stem || '—'}</span></div>
                <div class="edu-item"><strong>Habitat & Biotope</strong><span>${m.habitat || '—'}</span></div>
                <div class="edu-item"><strong>Période de pousse</strong><span>${m.season || '—'}</span></div>
                <div class="edu-item"><strong>Risque de confusion</strong><span>${m.confusion || '—'}</span></div>
            </div>

            <div class="edu-funfact" style="margin-top: 1.5rem; font-size: 0.92rem;">
                <strong>💡 Le saviez-vous ?</strong>
                <p style="margin-top: 0.25rem; color: var(--text-main);">${m.funFact || '—'}</p>
            </div>
        `;

        DOM.modalDetail.classList.remove('hidden');
    }

    function closeDetailModal() {
        DOM.modalDetail.classList.add('hidden');
    }

    // Modal Lightbox (Plein écran image)
    function openLightbox() {
        if (!AppState.questions || AppState.questions.length === 0) return;
        const currentQ = AppState.questions[AppState.currentIndex];
        if (!currentQ) return;

        SoundEngine.playClick();
        DOM.lightboxImg.src = currentQ.target.image;
        DOM.lightboxImg.onerror = () => { DOM.lightboxImg.src = currentQ.target.remoteImage; };
        DOM.lightboxCaption.textContent = AppState.isAnswered ? `${currentQ.target.name} (${currentQ.target.latin})` : 'Champignon mystère';
        DOM.lightboxBackdrop.classList.remove('hidden');
        AppState.lightboxActive = true;
    }

    function closeLightbox() {
        DOM.lightboxBackdrop.classList.add('hidden');
        AppState.lightboxActive = false;
    }

    // =========================================================================
    // Gestion des Événements & Raccourcis Clavier
    // =========================================================================

    function bindEvents() {
        // Thème & Son
        if (DOM.themeToggle) DOM.themeToggle.addEventListener('click', toggleTheme);
        if (DOM.soundToggle) DOM.soundToggle.addEventListener('click', toggleSound);

        // Logo retour accueil
        if (DOM.brandLogo) {
            DOM.brandLogo.addEventListener('click', (e) => {
                e.preventDefault();
                showScreen('setup');
            });
        }

        // Setup actions
        if (DOM.btnStartQuiz) DOM.btnStartQuiz.addEventListener('click', startQuiz);
        if (DOM.btnOpenMycoSetup) DOM.btnOpenMycoSetup.addEventListener('click', openMycothequeModal);
        if (DOM.btnOpenMycoNav) DOM.btnOpenMycoNav.addEventListener('click', openMycothequeModal);

        // Quiz actions
        if (DOM.btnNextQuestion) DOM.btnNextQuestion.addEventListener('click', nextQuestion);
        if (DOM.btnZoomImg) DOM.btnZoomImg.addEventListener('click', openLightbox);
        const imgWrapper = document.querySelector('.image-wrapper');
        if (imgWrapper) imgWrapper.addEventListener('click', openLightbox);

        // Bilan actions
        if (DOM.btnRestartQuiz) DOM.btnRestartQuiz.addEventListener('click', startQuiz);
        if (DOM.btnBilanToSetup) DOM.btnBilanToSetup.addEventListener('click', () => showScreen('setup'));
        if (DOM.btnOpenMycoBilan) DOM.btnOpenMycoBilan.addEventListener('click', openMycothequeModal);

        // Modals closing
        if (DOM.btnCloseMyco) DOM.btnCloseMyco.addEventListener('click', closeMycothequeModal);
        if (DOM.btnCloseDetail) DOM.btnCloseDetail.addEventListener('click', closeDetailModal);
        if (DOM.btnCloseLightbox) DOM.btnCloseLightbox.addEventListener('click', closeLightbox);

        // Fermeture sur clic arrière-plan
        DOM.modalMycotheque.addEventListener('click', (e) => {
            if (e.target === DOM.modalMycotheque) closeMycothequeModal();
        });
        DOM.modalDetail.addEventListener('click', (e) => {
            if (e.target === DOM.modalDetail) closeDetailModal();
        });
        DOM.lightboxBackdrop.addEventListener('click', (e) => {
            if (e.target === DOM.lightboxBackdrop) closeLightbox();
        });

        // Filtres Mycothèque
        if (DOM.mycoSearch) DOM.mycoSearch.addEventListener('input', renderMycothequeGrid);
        if (DOM.mycoFilter) DOM.mycoFilter.addEventListener('change', renderMycothequeGrid);

        // Raccourcis Clavier
        window.addEventListener('keydown', handleKeyboardShortcuts);
    }

    function handleKeyboardShortcuts(e) {
        // Fermer les modales avec Echap
        if (e.key === 'Escape') {
            if (!DOM.lightboxBackdrop.classList.contains('hidden')) {
                closeLightbox();
                return;
            }
            if (!DOM.modalDetail.classList.contains('hidden')) {
                closeDetailModal();
                return;
            }
            if (!DOM.modalMycotheque.classList.contains('hidden')) {
                closeMycothequeModal();
                return;
            }
        }

        // Si une modale est ouverte, on ignore les raccourcis de jeu
        if (!DOM.modalMycotheque.classList.contains('hidden') ||
            !DOM.modalDetail.classList.contains('hidden') ||
            !DOM.lightboxBackdrop.classList.contains('hidden')) {
            return;
        }

        // Si le quiz est actif
        if (!DOM.screenQuiz.classList.contains('hidden')) {
            // Touches 1, 2, 3, 4 pour répondre
            if (['1', '2', '3', '4'].includes(e.key) && !AppState.isAnswered) {
                const btn = DOM.optionsContainer.querySelector(`.option-btn[data-key="${e.key}"]`);
                if (btn) btn.click();
            }
            // Touche Espace ou Entrée pour passer à la question suivante
            else if ((e.key === ' ' || e.key === 'Enter') && AppState.isAnswered) {
                e.preventDefault();
                nextQuestion();
            }
            // Touche Z ou F pour ouvrir la visionneuse zoom
            else if (e.key.toLowerCase() === 'z' || e.key.toLowerCase() === 'f') {
                openLightbox();
            }
        }
    }

    // =========================================================================
    // Fonctions Utilitaires
    // =========================================================================

    function shuffleArray(arr) {
        const copy = [...arr];
        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    }

    // Démarrage au chargement du DOM
    document.addEventListener('DOMContentLoaded', init);

})();
