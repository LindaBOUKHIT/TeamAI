export async function loadDetector() {
    const worker = new Worker(new URL("./worker.js", import.meta.url), {
        type: "module",
    });
    const pending = new Map();
    let nextId = 0;
    let failure;

    function stop(error) {
        failure = error;
        worker.terminate();
        for (const { reject } of pending.values()) {
            reject(error);
        }
        pending.clear();
    }

    worker.addEventListener("error", () => {
        stop(new Error("Le moteur d'analyse en arrière-plan s'est arrêté."));
    });

    worker.addEventListener("messageerror", () => {
        stop(new Error("Impossible de lire la réponse du moteur d'analyse."));
    });

    worker.addEventListener("message", ({ data: { id, result, error } }) => {
        const request = pending.get(id);
        if (!request) return;

        pending.delete(id);
        if (error !== undefined) {
            request.reject(new Error(error));
        } else {
            request.resolve(result);
        }
    });

    function request(type, rows) {
        if (failure) return Promise.reject(failure);

        const id = ++nextId;
        return new Promise((resolve, reject) => {
            pending.set(id, { resolve, reject });
            try {
                worker.postMessage({ id, type, rows });
            } catch (error) {
                pending.delete(id);
                reject(error);
            }
        });
    }

    try {
        const info = await request("load");
        return { ...info, predict: (rows) => request("predict", rows) };
    } catch (error) {
        stop(error);
        throw error;
    }
}