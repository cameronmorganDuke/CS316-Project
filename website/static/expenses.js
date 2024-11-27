// estimateExpenses.js

const ETJ_TAX_RATE = {
    'DURHAM CITY': 1.3099,
    'DURHAM COUNTY': 0.7522,
    'DURHAM COUNTY,DURHAM CITY': 1.3099,
    'CHAPEL-HILL': 0.82,
    'RALEIGH': 0.98,
    'DURHAM COUNTY,RALEIGH': 0.98,
    'DURHAM COUNTY,MORRISVILLE': 0.75,
    'MORRISVILLE': 0.75,
    'CHAPEL-HILL,DURHAM CITY': 1.3099,
    'CARY': 1.15,
    'CHAPEL-HILL,DURHAM COUNTY': 0.82
};

const MANAGEMENT_RESERVE_PCT = 0.08;
const MAINTENENCE_RESERVE_PCT = 0.04;

const ELECTRIC_PER_KWH = 13.72;
const KWH_USAGE_PER_SQFT = 12;
const ELECTRIC_PER_SQFT = ELECTRIC_PER_KWH * KWH_USAGE_PER_SQFT;

const WATER_TIERS = { 2: 2.45, 5: 3.69, 8: 4.05, 15: 5.28, "else": 7.4 };
const SEWER_COST_PER_CCF = 5.26;
const WATER_USAGE_PER_OCCUPANT = [3, 4];

const GARBAGE_COST_PER_UNIT = 24;
const INSURANCE_COST_PCT = 0.005;
const NATURAL_GAS_PER_SQFT_PER_HR = 0.00049836;
const ELECTRIC_PER_SQFT_PER_HR = 0.0015463;
const LAWN_CARE_PER_ACRE = [100, 1600];
const LEGAL_AND_PROFESSIONAL_PCT = 0.015;

function estimateWaterCost(numOccupants) {
    const avgUsage = (WATER_USAGE_PER_OCCUPANT[0] + WATER_USAGE_PER_OCCUPANT[1]) / 2;
    let totalUsage = avgUsage * numOccupants;
    let cost = totalUsage * SEWER_COST_PER_CCF;
    let remainingUsage = totalUsage;

    Object.keys(WATER_TIERS).sort((a, b) => a - b).forEach(limit => {
        if (remainingUsage > 0) {
            const tierLimit = (typeof limit === 'number') ? parseFloat(limit) : Infinity;
            const usageInTier = Math.min(tierLimit, remainingUsage);
            cost += usageInTier * WATER_TIERS[limit];
            remainingUsage -= usageInTier;
        }
    });
    return cost;
}

function estimateGarbageCost(numUnits, include) {
    return include ? GARBAGE_COST_PER_UNIT * numUnits : 0;
}

function estimateUnits(zoningCode, lotSizeAcres = 1) {
    if (zoningCode.startsWith('PDR')) {
        const unitsPerAcre = parseFloat(zoningCode.split(' ')[1]);
        return Math.max(Math.floor(unitsPerAcre * lotSizeAcres), 1);
    }
    if (zoningCode.startsWith('RS')) {
        const minLotSizeSqft = parseInt(zoningCode.split('-')[1]) * 1000;
        return Math.max(Math.floor((lotSizeAcres * 43560) / minLotSizeSqft), 1);
    }
    if (zoningCode.startsWith('RU-5')) {
        const multiplier = parseInt(zoningCode.split('(')[1] || 1);
        return Math.max(Math.floor((lotSizeAcres * 43560) / (5000 / multiplier)), 1);
    }
    if (zoningCode.includes('MU') || zoningCode.includes('CC')) {
        return Math.max(Math.floor(10 * lotSizeAcres), 1);
    }
    return 1;
}

function estimateInsuranceCost(propertyValue) {
    return INSURANCE_COST_PCT * propertyValue;
}

function estimateHeatingCost(isGas, sqft) {
    const avgHours = 5;
    const daysInMonth = 30;
    return isGas ? NATURAL_GAS_PER_SQFT_PER_HR * avgHours * daysInMonth * sqft : ELECTRIC_PER_SQFT_PER_HR * avgHours * daysInMonth * sqft;
}

function estimateLegalCost(annualRentalIncome, numUnits) {
    return numUnits > 1 ? annualRentalIncome * LEGAL_AND_PROFESSIONAL_PCT : 0;
}

function managementReserveCost(propertyValue) {
    return propertyValue * MANAGEMENT_RESERVE_PCT;
}

function maintenenceReserveCost(propertyValue) {
    return propertyValue * MAINTENENCE_RESERVE_PCT;
}

function calculatePropertyTax(etj, propertyValue) {
    const taxRate = ETJ_TAX_RATE[etj] || 0;
    return (taxRate / 100) * propertyValue;
}

function calculateLawnSnowCost(acres) {
    const avgLawnCareCost = (LAWN_CARE_PER_ACRE[0] + LAWN_CARE_PER_ACRE[1]) / 2;
    return acres * avgLawnCareCost;
}

function estimateExpenses(annualRentalIncome, numUnits, isGas, sqft, propertyValue, numBeds, etj, acres, legal, utilities, maintenencePct, managementPct) {
    const costs = [
        legal ? legal: estimateLegalCost(annualRentalIncome, numUnits),
        utilities ? utilities: estimateHeatingCost(isGas, sqft),
        utilities ? 0: estimateInsuranceCost(propertyValue),
        utilities ? 0: estimateGarbageCost(numUnits, true),
        utilities ? 0: estimateWaterCost(numBeds),
        managementPct ? managementPct*annualRentalIncome : managementReserveCost(annualRentalIncome),
        maintenencePct ? maintenencePct*annualRentalIncome : maintenenceReserveCost(annualRentalIncome),
        calculatePropertyTax(etj, propertyValue),
        utilities ? 0: calculateLawnSnowCost(acres)
    ];
    console.log(estimateLegalCost(annualRentalIncome, numUnits))
    return costs.reduce((total, cost) => total + cost, 0);
}

// function gradeHouse(capRate, noi, propertyValue, monthlyRent, vacancyAllowance, numUnits, sqft, neighborhoodScore, expenses, zoningScore) {
    

//     // Define weights for each factor
//     const weights = {
//         capRate: 0.03,          // Reduce by factor of 10
//         noi: 0.02,              // Reduce by factor of 10
//         propertyValue: -0.01,   // Reduce by factor of 10
//         monthlyRent: 0.02,      // Reduce by factor of 10
//         vacancyAllowance: -0.005, // Reduce by factor of 10
//         numUnits: 0.01,         // Reduce by factor of 10
//         sqft: 0.005,            // Reduce by factor of 10
//         neighborhood: 0.01,     // Reduce by factor of 10
//         expenses: -0.02,        // Reduce by factor of 10
//         zoning: 0.005           // Reduce by factor of 10
//     };
    

//     // Calculate the score with weights applied
//     const score = (
//         weights.capRate * capRate +
//         weights.noi * noi +
//         weights.propertyValue * (1 / propertyValue) +  // Inverse for lower value preference
//         weights.monthlyRent * monthlyRent +
//         weights.vacancyAllowance * (1 - vacancyAllowance) +
//         weights.numUnits * numUnits +
//         weights.sqft * sqft +
//         // weights.neighborhood * neighborhoodScore +
//         weights.expenses * (1 / expenses)  // Inverse for lower expenses
//         // weights.zoning * zoningScore
//     );

//     // Define realistic min and max scores for normalization
//     const minScore = 0;  // Minimum expected scaled-down score
//     const maxScore = 10; // Maximum expected scaled-down score

//     // Normalize to 1–100
//     const normalizedScore = 1 + ((score - minScore) / (maxScore - minScore)) * 99;
//     // const finalScore = Math.min(100, Math.max(1, normalizedScore));
//     const k = -1/30
//     const x0 = 100
//     const finalScore = 100 / (1 + Math.exp(k*(score - x0)))
    

//     // Assign grade based on score ranges
//     let grade;
//     if (finalScore >= 90) {
//         grade = 'A';
//     } else if (finalScore >= 75) {
//         grade = 'B';
//     } else if (finalScore >= 60) {
//         grade = 'C';
//     } else if (finalScore >= 40) {
//         grade = 'D';
//     } else {
//         grade = 'F';
//     }

//     return { grade, score, finalScore };
// }

function gradeHouse(capRate, noi, propertyValue, monthlyRent, vacancyAllowance, numUnits, sqft, neighborhoodScore, expenses, zoningScore) {
    // Industry standard metrics
    const annualRent = monthlyRent * 12 * numUnits;
    const rentPerSqft = (monthlyRent * 12) / sqft;
    const expenseRatio = expenses / annualRent;
    const pricePerUnit = propertyValue / numUnits;
    const pricePerSqft = propertyValue / sqft;
    
    // Scoring criteria based on industry standards
    const metrics = {
        capRate: {
            weight: 0.25,
            score: () => {
                // Cap rate scoring (relaxed range 3-8%)
                if (capRate < 1) return 0;
                if (capRate > 6) return 100;
                return ((capRate - 1) / 5) * 100;
            }
        },
        expenseRatio: {
            weight: 0.15,
            score: () => {
                // Expense ratio scoring (relaxed range 35-60%)
                if (expenseRatio > 0.75) return 0;
                if (expenseRatio < 0.35) return 100;
                return ((0.75 - expenseRatio) / 0.40) * 100;
            }
        },
        rentPerSqft: {
            weight: 0.15,
            score: () => {
                // Rent per sqft scoring (lowered thresholds)
                const annualRentPerSqft = rentPerSqft;
                if (annualRentPerSqft < 8) return 0;
                if (annualRentPerSqft > 24) return 100;
                return ((annualRentPerSqft - 8) / 16) * 100;
            }
        },
        pricePerUnit: {
            weight: 0.15,
            score: () => {
                // Price per unit scoring (increased range)
                if (pricePerUnit > 350000) return 0;
                if (pricePerUnit < 75000) return 100;
                return ((350000 - pricePerUnit) / 275000) * 100;
            }
        },
        vacancyRate: {
            weight: 0.15,
            score: () => {
                // Vacancy allowance scoring (relaxed range 5-15%)
                if (vacancyAllowance > 15) return 0;
                if (vacancyAllowance < 5) return 100;
                return ((15 - vacancyAllowance) / 10) * 100;
            }
        },
        cashOnCash: {
            weight: 0.15,
            score: () => {
                // Cash on Cash Return (lowered thresholds)
                const downPayment = propertyValue * 0.25;
                const cashOnCash = (noi / downPayment) * 100;
                if (cashOnCash < 5) return 0;
                if (cashOnCash > 15) return 100;
                return ((cashOnCash - 5) / 10) * 100;
            }
        }
    };

    // Calculate weighted score
    let weightedTotal = 0;
    let weightSum = 0;

    for (const [key, metric] of Object.entries(metrics)) {
        const metricScore = metric.score();
        weightedTotal += metricScore * metric.weight;
        weightSum += metric.weight;
    }

    // Calculate final score (0-100 scale)
    const finalScore = weightedTotal / weightSum;

    // More generous grade ranges
    let grade;
    if (finalScore >= 85) {
        grade = finalScore >= 95 ? 'A+' : finalScore >= 90 ? 'A' : 'A-';
    } else if (finalScore >= 70) {
        grade = finalScore >= 80 ? 'B+' : finalScore >= 75 ? 'B' : 'B-';
    } else if (finalScore >= 55) {
        grade = finalScore >= 65 ? 'C+' : finalScore >= 60 ? 'C' : 'C-';
    } else if (finalScore >= 40) {
        grade = finalScore >= 50 ? 'D+' : finalScore >= 45 ? 'D' : 'D-';
    } else {
        grade = 'F';
    }

    // Return detailed scoring breakdown
    return {
        grade,
        score: weightedTotal,
        finalScore,
        metrics: Object.entries(metrics).reduce((acc, [key, metric]) => {
            acc[key] = {
                score: metric.score(),
                weight: metric.weight
            };
            return acc;
        }, {})
    };
}