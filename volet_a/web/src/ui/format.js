/**
 * SCRUM-65 : formats d'affichage. Les valeurs complètes restent dans le CSV
 * et dans l'info-bulle des scores ; l'écran montre deux décimales.
 */

const integer = new Intl.NumberFormat("fr-FR");
const decimal = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

export function formatInteger(value) {
    return integer.format(value);
}

export function formatDecimal(value) {
    return decimal.format(value);
}

/** « 1 bloc », « 3 blocs », « 0 bloc » (usage français : singulier pour 0 et 1). */
export function plural(count, singular, pluralForm = `${singular}s`) {
    return `${formatInteger(count)} ${Math.abs(count) < 2 ? singular : pluralForm}`;
}
