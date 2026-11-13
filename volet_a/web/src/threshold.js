import { loadDetector } from "./model.js";

const button = document.querySelector("#run");
const results = document.querySelector("#results");

button.addEventListener("click", async () => {
    button.disabled = true;
    results.textContent = "Chargement…";

    try {
        const detector = await loadDetector();
        const response = await fetch(
            `${import.meta.env.BASE_URL}model/threshold_cases.json`,
            { cache: "no-cache" }
        );
        if (!response.ok) {
            throw new Error(`Cas indisponibles : HTTP ${response.status}`);
        }
        const cases = await response.json();

        if (
            cases.split !== "val" ||
            cases.model_sha256 !== detector.meta.model_sha256 ||
            cases.threshold !== detector.meta.threshold
        ) {
            throw new Error("Cas incompatibles avec le modèle ou son seuil.");
        }

        const threshold = detector.meta.threshold;
        const lines = [
            `Seuil lu dans detector.meta.json : ${threshold}`,
            `Source du modèle : ${detector.source}`,
        ];
        let maxError = 0;
        let disagreements = 0;

        for (const size of [1, 3, 10]) {
            const scores = await detector.predict(cases.event_ids.slice(0, size));
            lines.push(`\nBatch ${size}`);

            scores.forEach((score, index) => {
                const expected = cases.p_anomaly[index];
                const label = Number(score >= threshold);
                const expectedLabel = cases.expected_labels[index];

                maxError = Math.max(maxError, Math.abs(score - expected));
                if (label !== expectedLabel) disagreements++;

                lines.push(
                    `${cases.block_ids[index]} : ` +
                    `Python=${expected.toPrecision(17)} ; ` +
                    `Web=${score.toPrecision(17)} ; ` +
                    `classe=${label} ; attendue=${expectedLabel}`
                );
            });
        }

        lines.push(
            `\nÉcart maximal : ${maxError.toExponential(6)}`,
            `Différences de classification : ${disagreements}`,
            maxError < cases.tolerance && disagreements === 0
                ? "SUCCÈS : scores et classes cohérents au nouveau seuil."
                : "ÉCHEC : vérifier les différences avant publication."
        );

        results.textContent = lines.join("\n");
    } catch (error) {
        results.textContent = `ERREUR : ${error.message}`;
        console.error(error);
    } finally {
        button.disabled = false;
    }
});
