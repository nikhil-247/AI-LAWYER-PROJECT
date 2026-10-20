import { useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { AlertTriangle, FileText, ShieldCheck } from "lucide-react";

interface CaseChecklistResponse {
  assessment_status: "educational_checklist_only";
  possible_outcome: {
    probability: string;
    result: string;
    basis: string;
  };
  inputs: {
    evidence_strength: string;
    past_record: string;
  };
  key_factors: string[];
  next_steps: string[];
  disclaimer: string;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/, "");

export default function CaseOutcomePredictor() {
  const [loading, setLoading] = useState(false);
  const [evidence, setEvidence] = useState("Moderate");
  const [pastRecord, setPastRecord] = useState("None");
  const [assessment, setAssessment] = useState<CaseChecklistResponse | null>(null);
  const [error, setError] = useState("");

  const handleAssess = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAssessment(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/case/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evidence_strength: evidence,
          past_record: pastRecord,
        }),
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const message = payload && typeof payload.error === "string"
          ? payload.error
          : "The checklist service returned an error.";
        throw new Error(message);
      }

      if (!payload || payload.assessment_status !== "educational_checklist_only") {
        throw new Error("The service returned an unexpected response.");
      }
      setAssessment(payload as CaseChecklistResponse);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "The checklist service is unavailable. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 py-12">
        <div className="max-w-5xl mx-auto px-4">
          <h1 className="text-3xl md:text-4xl text-[#1a2847] mb-2">
            Case Factors Checklist
          </h1>
          <p className="text-gray-600 mb-8">
            An educational checklist for organizing questions to discuss with a qualified lawyer.
          </p>

          <Card className="mb-8 bg-amber-50 border-amber-200">
            <CardContent className="p-6 flex gap-3">
              <AlertTriangle className="w-7 h-7 text-amber-700 shrink-0" />
              <div className="text-sm text-amber-900">
                <strong>This is not a case predictor.</strong> The tool does not estimate conviction,
                acquittal, or any probability. Do not enter names or confidential case details.
                It is not legal advice and may not reflect current law.
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <CardHeader className="bg-[#1a2847] text-white">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Checklist inputs
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <form onSubmit={handleAssess} className="space-y-5">
                  <div>
                    <Label>Self-assessed evidence strength</Label>
                    <Select value={evidence} onValueChange={setEvidence}>
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Limited">Limited</SelectItem>
                        <SelectItem value="Moderate">Moderate</SelectItem>
                        <SelectItem value="Strong">Strong</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Past record (if relevant)</Label>
                    <Select value={pastRecord} onValueChange={setPastRecord}>
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="None">None</SelectItem>
                        <SelectItem value="Minor">Minor</SelectItem>
                        <SelectItem value="Serious">Serious</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button type="submit" className="w-full bg-[#1a2847]" disabled={loading}>
                    <FileText className="w-5 h-5 mr-2" />
                    {loading ? "Preparing checklist..." : "Prepare checklist"}
                  </Button>
                </form>
                {error && (
                  <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="bg-indigo-600 text-white">
                <CardTitle className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5" />
                  Educational checklist
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-5" aria-live="polite">
                {assessment ? (
                  <>
                    <div>
                      <h2 className="font-semibold mb-1">Outcome assessment</h2>
                      <p className="text-gray-800 font-medium">No outcome or probability is calculated.</p>
                      <p className="text-sm text-gray-600 mt-2">{assessment.possible_outcome.basis}</p>
                    </div>
                    <div>
                      <h2 className="font-semibold mb-2">General factors to discuss</h2>
                      <ul className="space-y-2 text-sm text-gray-700 list-disc pl-5">
                        {assessment.key_factors.map((factor) => <li key={factor}>{factor}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h2 className="font-semibold mb-2">Suggested next steps</h2>
                      <ol className="space-y-2 text-sm text-gray-700 list-decimal pl-5">
                        {assessment.next_steps.map((step) => <li key={step}>{step}</li>)}
                      </ol>
                    </div>
                    <p className="text-xs text-gray-500">{assessment.disclaimer}</p>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">
                    Choose the available labels and prepare a general checklist. The inputs are not enough
                    to assess a real case, and the result will not predict an outcome.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card className="mt-8 bg-yellow-50 border-yellow-200">
            <CardContent className="p-4 flex gap-2 text-sm text-yellow-900">
              <ShieldCheck className="w-5 h-5 shrink-0" />
              Consult a qualified lawyer for real legal matters and verify applicable law against current official sources.
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}
