import * as ort from "onnxruntime-web";

ort.env.wasm.numThreads = 1;

const button = document.querySelector("#run");
const results = document.querySelector("#results");

button.addEventListener("click", async () => {
    button.disabled = true;
    results.textContent = "Chargement du modèle…";
    let session;

    try {
        const response = await fetch("./model/spike_cases.json");
        if (!response.ok) {
            throw new Error(`Chargement des cas : HTTP ${response.status}`);
        }
        const cases = await response.json();

        const startLoading = performance.now();
        session = await ort.InferenceSession.create(
            "./model/detector.onnx",
            { executionProviders: ["wasm"] }
        );
        const loadingMs = performance.now() - startLoading;

        const lines = [
            `Chargement et préparation : ${loadingMs.toFixed(1)} ms`,
        ];
        let maximumError = 0;

        // Vérifie également le batch dynamique dans le navigateur.
        for (const batchSize of [1, 3, 10]) {
            const values = cases.event_ids
                .slice(0, batchSize)
                .flat()
                .map((value) => BigInt(value));

            const input = new ort.Tensor(
                "int64",
                BigInt64Array.from(values),
                [batchSize, 50]
            );

            const startInference = performance.now();
            const outputs = await session.run({ event_ids: input });
            const inferenceMs = performance.now() - startInference;
            const prediction = outputs.p_anomaly;

            if (
                prediction.type !== "float32" ||
                prediction.dims.length !== 1 ||
                prediction.dims[0] !== batchSize
            ) {
                throw new Error("La sortie ne respecte pas le contrat C3.");
            }

            lines.push(`\nBatch ${batchSize} : ${inferenceMs.toFixed(1)} ms`);

            for (let i = 0; i < batchSize; i++) {
                const actual = Number(prediction.data[i]);
                const expected = cases.p_anomaly[i];
                const error = Math.abs(actual - expected);

                if (!Number.isFinite(actual)) {
                    throw new Error(`Résultat invalide pour l’entrée ${i + 1}`);
                }

                maximumError = Math.max(maximumError, error);

                if (batchSize === 10) {
                    lines.push(
                        `Entrée ${i + 1} : Python=${expected.toFixed(8)} ; ` +
                        `Web=${actual.toFixed(8)} ; écart=${error.toExponential(2)}`
                    );
                }
            }
        }

        lines.push(`\nÉcart maximal : ${maximumError.toExponential(4)}`);
        lines.push(
            maximumError < cases.tolerance
                ? "SUCCÈS : parité Python / navigateur validée."
                : "ÉCHEC : écart supérieur ou égal à la tolérance."
        );

        results.textContent = lines.join("\n");
    } catch (error) {
        results.textContent = `ERREUR : ${error.message}`;
        console.error(error);
    } finally {
        if (session) await session.release();
        button.disabled = false;
    }
});