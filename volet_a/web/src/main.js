import { loadDetector } from "./model.js";
import { compileVocab, encode } from "./preprocess.js";

const status = document.querySelector("#status");
const warning = document.querySelector("#warning");
const button = document.querySelector("#run");
const results = document.querySelector("#results");

async function start() {
    try {
        const detector = await loadDetector();
        const vocab = compileVocab(detector.vocab);

        status.textContent =
            `Modèle chargé — version ${detector.meta.version} — ` +
            `source : ${detector.source}.`;

        if (detector.isToy) {
            warning.hidden = false;
            warning.textContent =
                "MODÈLE FACTICE : poids aléatoires, aucun entraînement. " +
                "Les scores servent uniquement à vérifier le fonctionnement technique. " +
                "Ils ne permettent pas de détecter une anomalie réelle.";
        }

        results.textContent = "Prêt. Cliquez sur le bouton pour tester.";
        button.disabled = false;

        button.addEventListener("click", async () => {
            button.disabled = true;
            results.textContent = "Inférence en cours…";

            try {
                // Séquence artificielle : aucun jeu de test officiel utilisé.
                const events = ["E5", "E22", "E5", "E11"];
                const encoded = encode(events, vocab);

                const startTime = performance.now();
                const [score] = await detector.predict([encoded.ids]);
                const elapsed = performance.now() - startTime;

                const lines = [
                    `Entrée artificielle : ${events.join(", ")}`,
                    `Forme de l’entrée : [1, ${encoded.ids.length}]`,
                    `Score de sortie : ${score.toFixed(8)}`,
                    `Temps d’inférence : ${elapsed.toFixed(1)} ms`,
                ];

                if (detector.isToy) {
                    lines.push(
                        "Modèle factice : aucune interprétation normal/anomalie."
                    );
                } else {
                    lines.push(
                        `Seuil : ${detector.meta.threshold}`,
                        `Classe : ${score >= detector.meta.threshold ? "anomalie" : "normal"
                        }`,
                        "Le score n’est pas une probabilité calibrée."
                    );
                }

                results.textContent = lines.join("\n");
            } catch (error) {
                results.textContent = `Erreur : ${error.message}`;
                console.error(error);
            } finally {
                button.disabled = false;
            }
        });
    } catch (error) {
        status.textContent = "Échec du chargement.";
        results.textContent = `Erreur : ${error.message}`;
        console.error(error);
    }
}

start();