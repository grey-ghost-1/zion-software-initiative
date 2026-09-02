"use client";

import { useId, useState } from "react";
import type {
  HavenConcernCategory,
  HavenConcernDuration,
  HavenNavigationResponse,
  HavenReviewReasonCode,
  HavenSeverity,
} from "@zion/api-client";
import { localHavenEngine, type HavenDemoEngine } from "@/lib/haven-demo";

const CATEGORY_OPTIONS: Array<{ value: HavenConcernCategory; label: string }> = [
  { value: "fever_or_flu", label: "Fever or flu-like symptoms" },
  { value: "cough_or_cold", label: "Cough or cold" },
  { value: "stomach_trouble", label: "Stomach trouble" },
  { value: "minor_injury", label: "Minor injury" },
  { value: "medication_instructions", label: "Understanding medication instructions" },
  { value: "stress_or_anxiety", label: "Stress or anxiety" },
  { value: "low_mood", label: "Low mood" },
  { value: "sleep_trouble", label: "Sleep trouble" },
  { value: "cost_or_coverage", label: "Cost of care or coverage" },
  { value: "general_question", label: "General health question" },
];

const DURATION_OPTIONS: Array<{ value: HavenConcernDuration; label: string }> = [
  { value: "under_one_day", label: "Less than a day" },
  { value: "one_to_three_days", label: "1–3 days" },
  { value: "four_to_seven_days", label: "4–7 days" },
  { value: "over_one_week", label: "More than a week" },
];

const SEVERITY_OPTIONS: Array<{ value: HavenSeverity; label: string }> = [
  { value: "mild", label: "Mild — barely affects my day" },
  { value: "moderate", label: "Moderate — gets in the way of my day" },
  { value: "severe", label: "Severe — I cannot do my usual activities" },
];

const REASON_CODE_OPTIONS: Array<{ value: HavenReviewReasonCode; label: string }> = [
  { value: "routing_confirmed", label: "Routing confirmed" },
  { value: "routing_too_cautious", label: "Routing too cautious" },
  { value: "routing_not_cautious_enough", label: "Routing not cautious enough" },
  { value: "resource_link_problem", label: "Resource link problem" },
  { value: "demo_walkthrough_complete", label: "Demo walkthrough complete" },
];

const OUTCOME_LABELS: Record<string, string> = {
  emergency_now: "Emergency guidance",
  crisis_support_now: "Crisis support guidance",
  clinician_soon: "Talk with a clinician soon",
  mental_health_support: "Mental-health support options",
  low_cost_care_routing: "Low-cost care routing",
  self_care_education: "Self-care education",
};

type DemoPhase = "idle" | "loading" | "routed" | "closed" | "error";

interface HavenDemoProps {
  /** Injectable for tests; defaults to the deterministic in-browser engine. */
  engine?: HavenDemoEngine;
}

export function HavenDemo({ engine = localHavenEngine }: HavenDemoProps) {
  const formId = useId();
  const [phase, setPhase] = useState<DemoPhase>("idle");
  const [category, setCategory] = useState<HavenConcernCategory>("cough_or_cold");
  const [duration, setDuration] = useState<HavenConcernDuration>("one_to_three_days");
  const [severity, setSeverity] = useState<HavenSeverity>("mild");
  const [immediateDanger, setImmediateDanger] = useState(false);
  const [selfHarmRisk, setSelfHarmRisk] = useState(false);
  const [concernText, setConcernText] = useState("");
  const [result, setResult] = useState<HavenNavigationResponse | null>(null);
  const [reasonCode, setReasonCode] = useState<HavenReviewReasonCode>("routing_confirmed");
  const [reviewedWith, setReviewedWith] = useState<HavenReviewReasonCode | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPhase("loading");
    setReviewedWith(null);
    try {
      const response = await engine.submit({
        concern_category: category,
        duration,
        severity,
        immediate_danger: immediateDanger,
        self_harm_risk: selfHarmRisk,
        concern_text: concernText.trim() === "" ? undefined : concernText.trim(),
      });
      setResult(response);
      setPhase("routed");
    } catch {
      setResult(null);
      setPhase("error");
    }
  }

  function handleReset() {
    setPhase("idle");
    setResult(null);
    setReviewedWith(null);
    setImmediateDanger(false);
    setSelfHarmRisk(false);
    setConcernText("");
  }

  return (
    <div className="haven-demo">
      <form aria-label="Synthetic concern demonstration" onSubmit={handleSubmit}>
        <p>
          Everything below runs in your browser with synthetic scenarios only. Nothing you
          enter is sent, stored, or reviewed by anyone.
        </p>

        <p>
          <label htmlFor={`${formId}-category`}>
            What kind of concern is this scenario about?
          </label>
          <br />
          <select
            id={`${formId}-category`}
            value={category}
            onChange={(event) => setCategory(event.target.value as HavenConcernCategory)}
          >
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </p>

        <p>
          <label htmlFor={`${formId}-duration`}>How long has it been going on?</label>
          <br />
          <select
            id={`${formId}-duration`}
            value={duration}
            onChange={(event) => setDuration(event.target.value as HavenConcernDuration)}
          >
            {DURATION_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </p>

        <p>
          <label htmlFor={`${formId}-severity`}>How much does it affect daily activities?</label>
          <br />
          <select
            id={`${formId}-severity`}
            value={severity}
            onChange={(event) => setSeverity(event.target.value as HavenSeverity)}
          >
            {SEVERITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </p>

        <fieldset>
          <legend>Safety check — these always come first</legend>
          <p>
            <input
              id={`${formId}-danger`}
              type="checkbox"
              checked={immediateDanger}
              onChange={(event) => setImmediateDanger(event.target.checked)}
            />{" "}
            <label htmlFor={`${formId}-danger`}>Someone is in immediate physical danger</label>
          </p>
          <p>
            <input
              id={`${formId}-self-harm`}
              type="checkbox"
              checked={selfHarmRisk}
              onChange={(event) => setSelfHarmRisk(event.target.checked)}
            />{" "}
            <label htmlFor={`${formId}-self-harm`}>I may hurt myself or someone else</label>
          </p>
        </fieldset>

        <p>
          <label htmlFor={`${formId}-text`}>
            Optional short description (synthetic scenario text, 280 characters max)
          </label>
          <br />
          <textarea
            id={`${formId}-text`}
            maxLength={280}
            rows={3}
            value={concernText}
            onChange={(event) => setConcernText(event.target.value)}
          />
        </p>

        <p>
          <button type="submit" disabled={phase === "loading"}>
            Get navigation options
          </button>{" "}
          <button type="button" onClick={handleReset}>
            Reset demonstration
          </button>
        </p>
      </form>

      <div aria-live="polite">
        {phase === "loading" ? <p role="status">Preparing deterministic routing…</p> : null}

        {phase === "error" ? (
          <p role="alert">
            The demonstration hit an unexpected error. In a real emergency, call 911; for
            crisis support, call or text 988.
          </p>
        ) : null}

        {phase !== "loading" && result ? (
          <div>
            {result.emergency.active ? (
              <div role="alert">
                <h4>{result.emergency.headline}</h4>
                <ul>
                  {result.emergency.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
                <p>{result.emergency.no_monitoring_note}</p>
              </div>
            ) : null}

            <h4>Routing outcome: {OUTCOME_LABELS[result.outcome] ?? result.outcome}</h4>
            <p>Synthetic scenario · stored: {result.stored ? "yes" : "no"}</p>
            <h5>Next-step options</h5>
            <ul>
              {result.next_steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>

            <h5>Curated resources</h5>
            {result.resources.length === 0 ? (
              <p>No curated resources matched this scenario.</p>
            ) : (
              <ul>
                {result.resources.map((resource) => (
                  <li key={resource.slug}>
                    <a href={resource.url}>{resource.name}</a> — {resource.description}{" "}
                    <span>
                      ({resource.jurisdiction}, reviewed {resource.reviewed_on},{" "}
                      {resource.source_mode === "live_official"
                        ? "official reference"
                        : "synthetic example"}
                      )
                    </span>
                  </li>
                ))}
              </ul>
            )}

            <h5>Plain-language cards</h5>
            {result.guidance_cards.length === 0 ? (
              <p>No plain-language card exists for this concern yet.</p>
            ) : (
              <ul>
                {result.guidance_cards.map((card) => (
                  <li key={card.slug}>
                    <h6>{card.title}</h6>
                    <p>
                      <strong>Original wording:</strong> {card.original_text}
                    </p>
                    <p>
                      <strong>Plain language:</strong> {card.plain_text}
                    </p>
                    <p>Source: {card.source_name}</p>
                  </li>
                ))}
              </ul>
            )}

            <p>{result.disclaimer}</p>

            {phase === "routed" ? (
              <div>
                <h5>Navigator review (demo)</h5>
                <p>
                  <label htmlFor={`${formId}-reason`}>Review reason code</label>
                  <br />
                  <select
                    id={`${formId}-reason`}
                    value={reasonCode}
                    onChange={(event) =>
                      setReasonCode(event.target.value as HavenReviewReasonCode)
                    }
                  >
                    {REASON_CODE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setReviewedWith(reasonCode);
                    setPhase("closed");
                  }}
                >
                  Review and close plan
                </button>
              </div>
            ) : null}

            {phase === "closed" ? (
              <p role="status">
                Demo plan reviewed with reason code “{reviewedWith}” and closed. Nothing was
                stored: reset the demonstration to run another synthetic scenario.
              </p>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
