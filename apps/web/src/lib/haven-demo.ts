/**
 * Deterministic, in-browser Haven demonstration engine.
 *
 * This mirrors the server's deterministic safety check and routing table
 * (apps/api/zion_api/services/haven_safety.py and haven_routing.py) using the
 * exact typed API contracts from `@zion/api-client`, so the page can run a
 * truthful, fully client-side demonstration: nothing is sent anywhere and
 * nothing is stored. The API remains the source of truth and is covered by
 * its own test suite; this module is covered by the web test suite.
 */

import type {
  HavenGuidanceCard,
  HavenNavigationRequest,
  HavenNavigationResponse,
  HavenResource,
  HavenRoutingOutcome,
} from "@zion/api-client";

export const NO_MONITORING_NOTE =
  "This demonstration does not monitor you, store what you typed, alert anyone, " +
  "or contact any service on your behalf. You must reach out directly.";

export const NON_DIAGNOSTIC_DISCLAIMER =
  "Haven is a demonstration, not a medical service. It does not provide " +
  "diagnosis, treatment, or medical advice. For medical questions, talk with a " +
  "licensed clinician.";

const EMERGENCY_HEADLINE = "If anyone is in immediate physical danger, call 911 now.";
const EMERGENCY_STEPS = [
  "Call 911 (United States) right away, or go to the nearest emergency room.",
  "If it is safe, stay with the person until help arrives.",
  "If you also need emotional crisis support, call or text 988 to reach the 988 Suicide & Crisis Lifeline.",
];

const CRISIS_HEADLINE =
  "If you may hurt yourself or someone else, contact the 988 Suicide & Crisis " +
  "Lifeline now — call or text 988, or chat at 988lifeline.org.";
const CRISIS_STEPS = [
  "Call or text 988 (United States) to reach the 988 Suicide & Crisis Lifeline, free and confidential, 24/7.",
  "Chat online at https://988lifeline.org/chat/.",
  "If there is immediate physical danger, call 911.",
];

// Conservative phrase lists mirroring the server. False positives only ever
// surface standard emergency guidance.
const CRISIS_PHRASES = [
  "suicide",
  "suicidal",
  "suicde",
  "sucide",
  "suiside",
  "kill myself",
  "kil myself",
  "killing myself",
  "end my life",
  "end it all",
  "ending it all",
  "take my own life",
  "dont want to be here anymore",
  "dont want to live",
  "no reason to live",
  "better off dead",
  "better off without me",
  "unalive",
  "self harm",
  "self harming",
  "hurt myself",
  "hurting myself",
  "harm myself",
  "cut myself",
  "cutting myself",
  "kms",
  "hurt someone else",
  "hurt somebody else",
  "kill someone",
  "kill somebody",
];

const EMERGENCY_PHRASES = [
  "chest pain",
  "chest pressure",
  "cant breathe",
  "can not breathe",
  "trouble breathing",
  "not breathing",
  "stopped breathing",
  "unconscious",
  "unresponsive",
  "seizure",
  "stroke",
  "heart attack",
  "severe bleeding",
  "bleeding wont stop",
  "choking",
  "overdose",
  "overdosed",
  "took too many pills",
  "poisoned",
  "throat closing",
  "gun",
  "knife",
  "weapon",
  "being attacked",
];

export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .replace(/['\u2019\u02bc`]/g, "")
    .normalize("NFKD")
    .replace(/[^\x20-\x7e]/g, " ")
    .replace(/[^a-z0-9 ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function containsPhrase(normalized: string, phrases: string[]): boolean {
  const padded = ` ${normalized} `;
  return phrases.some((phrase) => padded.includes(` ${phrase} `));
}

/** Curated demonstration content, mirrored from the API seed and clearly synthetic-scope. */
const DEMO_RESOURCES: HavenResource[] = [
  {
    slug: "988-lifeline",
    name: "988 Suicide & Crisis Lifeline",
    description:
      "Free, confidential crisis support in the United States, 24/7: call or text 988, or chat online.",
    url: "https://988lifeline.org/",
    kind: "crisis_support",
    jurisdiction: "US",
    provenance: "nonprofit_official",
    source_mode: "live_official",
    reviewed_on: "2026-09-01",
    retrieved_on: "2026-09-01",
    review_valid_until: "2027-03-01",
    freshness: "current",
  },
  {
    slug: "findtreatment-gov",
    name: "FindTreatment.gov",
    description:
      "SAMHSA's confidential locator for licensed mental-health and substance-use treatment providers.",
    url: "https://findtreatment.gov/",
    kind: "treatment_locator",
    jurisdiction: "US",
    provenance: "federal_agency",
    source_mode: "live_official",
    reviewed_on: "2026-09-01",
    retrieved_on: "2026-09-01",
    review_valid_until: "2027-03-01",
    freshness: "current",
  },
  {
    slug: "hrsa-find-a-health-center",
    name: "HRSA Find a Health Center",
    description:
      "HRSA's official locator for federally funded health centers that provide care on a sliding fee scale.",
    url: "https://findahealthcenter.hrsa.gov/",
    kind: "low_cost_care",
    jurisdiction: "US",
    provenance: "federal_agency",
    source_mode: "live_official",
    reviewed_on: "2026-09-01",
    retrieved_on: "2026-09-01",
    review_valid_until: "2027-03-01",
    freshness: "current",
  },
  {
    slug: "medlineplus",
    name: "MedlinePlus",
    description:
      "Plain-language health education from the National Library of Medicine (NIH).",
    url: "https://medlineplus.gov/",
    kind: "health_education",
    jurisdiction: "US",
    provenance: "federal_agency",
    source_mode: "live_official",
    reviewed_on: "2026-09-01",
    retrieved_on: "2026-09-01",
    review_valid_until: "2027-03-01",
    freshness: "current",
  },
];

const DEMO_CARDS: HavenGuidanceCard[] = [
  {
    slug: "fever-medicine-instructions",
    category: "fever_or_flu",
    title: "Understanding fever medicine label instructions",
    original_text:
      "For adults, acetaminophen 650 mg may be administered orally every 6 hours as needed " +
      "for fever of 100.4 F or higher. Do not exceed 3000 mg within 24 hours.",
    plain_text:
      "Adults can take acetaminophen 650 mg by mouth every 6 hours if a fever reaches " +
      "100.4 F or higher. Do not take more than 3000 mg within 24 hours.",
    source_name: "MedlinePlus (NIH) — acetaminophen label basics, paraphrased",
    source_url: "https://medlineplus.gov/druginfo/meds/a681004.html",
    jurisdiction: "US",
    reviewed_on: "2026-09-01",
  },
  {
    slug: "cold-self-care-and-warning-signs",
    category: "cough_or_cold",
    title: "Colds: self-care and when to get help",
    original_text:
      "Most colds resolve on their own within 7 to 10 days. Rest and maintain fluid intake. " +
      "Call 911 for trouble breathing, blue lips, or chest pain — these are emergency warning signs.",
    plain_text:
      "Most colds get better on their own in 7 to 10 days. Rest and drink fluids. Call 911 " +
      "right away for trouble breathing, blue lips, or chest pain — these are emergency warning signs.",
    source_name: "MedlinePlus (NIH) — common cold, paraphrased",
    source_url: "https://medlineplus.gov/commoncold.html",
    jurisdiction: "US",
    reviewed_on: "2026-09-01",
  },
  {
    slug: "stress-basics",
    category: "stress_or_anxiety",
    title: "Everyday stress and where support lives",
    original_text:
      "Feeling stressed or anxious is common. Slow breathing for 5 minutes can help in the " +
      "moment. If worry keeps you from daily activities for 2 weeks or more, talk with a " +
      "health professional. The 988 Lifeline provides free, confidential support.",
    plain_text:
      "Stress and anxious feelings are common. Try slow breathing for 5 minutes to help in " +
      "the moment. If worry keeps you from daily activities for 2 weeks or more, talk with a " +
      "health professional. The 988 Lifeline offers free, confidential support.",
    source_name: "MedlinePlus (NIH) — stress, paraphrased",
    source_url: "https://medlineplus.gov/stress.html",
    jurisdiction: "US",
    reviewed_on: "2026-09-01",
  },
];

const MENTAL_HEALTH_CATEGORIES = new Set(["stress_or_anxiety", "low_mood", "sleep_trouble"]);
const LONG_DURATIONS = new Set(["four_to_seven_days", "over_one_week"]);

const NEXT_STEPS: Record<HavenRoutingOutcome, string[]> = {
  emergency_now: ["Call 911 (United States) or go to the nearest emergency room now."],
  crisis_support_now: [
    "Call or text 988, or chat at 988lifeline.org, to reach the 988 Suicide & Crisis Lifeline now.",
  ],
  clinician_soon: [
    "Contact a clinician soon — for example a primary care office, urgent care clinic, or nurse advice line.",
    "If cost is a barrier, community health centers offer care on a sliding fee scale.",
    "Read the matching plain-language card below so you know which warning signs mean you should seek care right away.",
  ],
  mental_health_support: [
    "Consider talking with a mental-health professional; the treatment locator below lists licensed options.",
    "If things ever feel like too much, the 988 Lifeline is available any time by call, text, or chat.",
    "Trusted plain-language education about stress, mood, and sleep is linked below.",
  ],
  low_cost_care_routing: [
    "Use the health-center finder below to locate care offered on a sliding fee scale near you.",
    "Community health centers serve people regardless of ability to pay or insurance status.",
  ],
  self_care_education: [
    "Review the matching plain-language card below for trusted self-care basics.",
    "If symptoms last longer, get worse, or worry you, contact a clinician.",
  ],
};

const RESOURCE_KINDS: Record<HavenRoutingOutcome, string[]> = {
  emergency_now: ["crisis_support"],
  crisis_support_now: ["crisis_support", "treatment_locator"],
  clinician_soon: ["low_cost_care", "health_education"],
  mental_health_support: ["crisis_support", "treatment_locator", "health_education"],
  low_cost_care_routing: ["low_cost_care", "health_education"],
  self_care_education: ["health_education"],
};

export type Escalation = "none" | "emergency_911" | "crisis_988";

export function assessSafety(request: HavenNavigationRequest): Escalation {
  const normalized = request.concern_text ? normalizeText(request.concern_text) : "";
  const emergencyDetected = normalized !== "" && containsPhrase(normalized, EMERGENCY_PHRASES);
  const crisisDetected = normalized !== "" && containsPhrase(normalized, CRISIS_PHRASES);

  if (request.immediate_danger || emergencyDetected) {
    return "emergency_911";
  }
  if (request.self_harm_risk || crisisDetected) {
    return "crisis_988";
  }
  return "none";
}

function routeOutcome(request: HavenNavigationRequest, escalation: Escalation): HavenRoutingOutcome {
  if (escalation === "emergency_911") return "emergency_now";
  if (escalation === "crisis_988") return "crisis_support_now";
  if (MENTAL_HEALTH_CATEGORIES.has(request.concern_category)) return "mental_health_support";
  if (request.concern_category === "cost_or_coverage") return "low_cost_care_routing";
  if (request.severity === "severe") return "clinician_soon";
  if (request.severity === "moderate" && LONG_DURATIONS.has(request.duration)) {
    return "clinician_soon";
  }
  return "self_care_education";
}

export interface HavenDemoEngine {
  submit(request: HavenNavigationRequest): Promise<HavenNavigationResponse>;
}

/**
 * The default local engine: deterministic, synchronous logic wrapped in a
 * resolved promise. Nothing leaves the browser.
 */
export const localHavenEngine: HavenDemoEngine = {
  submit(request: HavenNavigationRequest): Promise<HavenNavigationResponse> {
    const escalation = assessSafety(request);
    const outcome = routeOutcome(request, escalation);

    const emergency =
      escalation === "none"
        ? {
            active: false,
            kind: null,
            headline: null,
            steps: [],
            no_monitoring_note: NO_MONITORING_NOTE,
          }
        : {
            active: true,
            kind: escalation,
            headline: escalation === "emergency_911" ? EMERGENCY_HEADLINE : CRISIS_HEADLINE,
            steps: escalation === "emergency_911" ? EMERGENCY_STEPS : CRISIS_STEPS,
            no_monitoring_note: NO_MONITORING_NOTE,
          };

    return Promise.resolve({
      synthetic: true,
      stored: false,
      emergency,
      outcome,
      next_steps: NEXT_STEPS[outcome],
      resources: DEMO_RESOURCES.filter((resource) =>
        RESOURCE_KINDS[outcome].includes(resource.kind),
      ),
      guidance_cards: DEMO_CARDS.filter((card) => card.category === request.concern_category),
      disclaimer: NON_DIAGNOSTIC_DISCLAIMER,
    });
  },
};
