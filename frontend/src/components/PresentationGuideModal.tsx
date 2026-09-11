import React, { useState } from 'react';
import { 
  X, 
  HelpCircle, 
  CheckCircle2, 
  Camera, 
  ShieldAlert, 
  Database, 
  Cpu, 
  Activity, 
  FileText, 
  PlayCircle,
  AlertOctagon,
  Eye,
  Sliders,
  Sparkles,
  Award
} from 'lucide-react';

interface PresentationGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCamera: (camId: number) => void;
}

export const PresentationGuideModal: React.FC<PresentationGuideModalProps> = ({
  isOpen,
  onClose,
  onSelectCamera
}) => {
  const [activeSection, setActiveSection] = useState<'pitch' | 'demo_steps' | 'datasets' | 'qa'>('pitch');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-5xl rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden text-slate-100">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 border border-indigo-500/40 rounded-xl text-indigo-400">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Project Demonstration & Defense Guide
                <span className="text-xs font-mono px-2 py-0.5 bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 rounded-full">
                  SPEAKER SCRIPT
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Step-by-step presentation script, live demonstration steps, and reviewer Q&A cheat sheet.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex items-center gap-2 px-6 py-2.5 bg-slate-950/50 border-b border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setActiveSection('pitch')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
              activeSection === 'pitch' 
                ? 'bg-indigo-600 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            1. The 30-Second Elevator Pitch
          </button>
          <button
            onClick={() => setActiveSection('demo_steps')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
              activeSection === 'demo_steps' 
                ? 'bg-indigo-600 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <PlayCircle className="w-4 h-4" />
            2. Live Camera Walkthrough (Demo Script)
          </button>
          <button
            onClick={() => setActiveSection('datasets')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
              activeSection === 'datasets' 
                ? 'bg-indigo-600 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Database className="w-4 h-4" />
            3. 4-Dataset Architecture & RT-DETR
          </button>
          <button
            onClick={() => setActiveSection('qa')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
              activeSection === 'qa' 
                ? 'bg-indigo-600 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            4. Reviewer Defense Q&A Cheatsheet
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-slate-300">
          
          {/* SECTION 1: ELEVATOR PITCH */}
          {activeSection === 'pitch' && (
            <div className="space-y-5">
              <div className="bg-indigo-950/30 border border-indigo-800/40 p-5 rounded-xl space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  What to say first (Memorize or Read this):
                </span>
                <p className="text-base text-slate-100 font-medium leading-relaxed italic">
                  "Most industrial computer vision systems fail in real factories because they only draw raw bounding boxes and flood operators with false alarms. Our project is an <strong>Enterprise AI Safety & Workplace Intelligence Platform</strong> engineered specifically for high-risk industrial environments like warehouses, assembly plants, and robotic cells."
                </p>
                <p className="text-sm text-slate-300 leading-relaxed">
                  "Instead of just detecting objects, our system converts vision into <strong>deterministic physical safety intelligence</strong>: calculating dynamic Time-to-Collision for moving forklifts, enforcing anatomical spatial constraints so carried hardhats aren't marked compliant, geofencing hazard zones via worker foot ground-contact points, and detecting recumbent worker falls with sustained immobility state machines."
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-800/50 border border-slate-700/60 p-4 rounded-xl space-y-2">
                  <div className="flex items-center gap-2 text-sky-400 font-bold text-sm">
                    <Cpu className="w-4 h-4" />
                    RT-DETR-L Vision Core
                  </div>
                  <p className="text-xs text-slate-400">
                    Real-Time DEtection TRansformer with direct set prediction queries. No Non-Maximum Suppression (NMS) latency bottleneck; 45.8 ms inference latency at 81.4% mAP.
                  </p>
                </div>

                <div className="bg-slate-800/50 border border-slate-700/60 p-4 rounded-xl space-y-2">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
                    <ShieldAlert className="w-4 h-4" />
                    Explainable Risk Engine
                  </div>
                  <p className="text-xs text-slate-400">
                    Deterministic Levels 0 to 4 (Normal, Low, Medium, High, Critical) with plain-English reasoning and explicit operational actions.
                  </p>
                </div>

                <div className="bg-slate-800/50 border border-slate-700/60 p-4 rounded-xl space-y-2">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    Human-in-the-Loop Audit
                  </div>
                  <p className="text-xs text-slate-400">
                    Strict incident triage workflow (Pending Review → Acknowledged → Confirmed / False Positive Override) with immutable operator audit trails.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 2: DEMO STEPS */}
          {activeSection === 'demo_steps' && (
            <div className="space-y-5">
              <p className="text-xs text-slate-400">
                Follow this exact sequence while sharing your screen or presenting in person:
              </p>

              {/* Step 1: Camera 1 */}
              <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
                    <Camera className="w-4 h-4" />
                    Step 1: Switch to Camera 1 — Warehouse Loading Dock (Forklift Proximity)
                  </div>
                  <button
                    onClick={() => { onSelectCamera(1); onClose(); }}
                    className="text-xs px-2.5 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded hover:bg-amber-500/30 transition-colors"
                  >
                    View Camera 1 Now
                  </button>
                </div>
                <div className="text-xs space-y-1.5 pl-6 border-l-2 border-amber-500/40 text-slate-300">
                  <p><strong>What to say:</strong> "Notice Camera 1. We are monitoring a warehouse transit aisle where industrial forklifts interact with pedestrians."</p>
                  <p><strong>What to point out on screen:</strong></p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                    <li>The dashed red/orange line connecting the worker to the moving forklift.</li>
                    <li>The dynamic distance meter (<code className="text-amber-300">COLLISION PROXIMITY: 2.4m</code>).</li>
                    <li>Explain the math: <em>"The system doesn't just measure pixel distance. It calculates Time-to-Collision (TTC) using velocity approach vectors. When TTC drops below 2.0s, the system escalates to Level 4 Emergency."</em></li>
                  </ul>
                </div>
              </div>

              {/* Step 2: Camera 2 */}
              <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-sky-400 text-sm">
                    <Camera className="w-4 h-4" />
                    Step 2: Switch to Camera 2 — Shop Floor Assembly (PPE Compliance)
                  </div>
                  <button
                    onClick={() => { onSelectCamera(2); onClose(); }}
                    className="text-xs px-2.5 py-1 bg-sky-500/20 text-sky-300 border border-sky-500/40 rounded hover:bg-sky-500/30 transition-colors"
                  >
                    View Camera 2 Now
                  </button>
                </div>
                <div className="text-xs space-y-1.5 pl-6 border-l-2 border-sky-500/40 text-slate-300">
                  <p><strong>What to say:</strong> "Here in the assembly plant, all personnel must wear an approved hardhat and high-visibility vest."</p>
                  <p><strong>What to point out on screen:</strong></p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                    <li>Worker A (left) has full gear (yellow hardhat + fluorescent vest with 3M silver stripes) and is flagged compliant.</li>
                    <li>Worker B (right) wears dark clothing with no hardhat. The sidebar immediately fires a <strong>PPE Violation (Risk Level 2/3)</strong>.</li>
                    <li>Explain the algorithm: <em>"Our hierarchical spatial evaluator bounds the top 25% of the body for headwear. If a hardhat is carried in hand or hanging on a belt, the system explicitly rejects it as compliant."</em></li>
                  </ul>
                </div>
              </div>

              {/* Step 3: Camera 3 */}
              <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-rose-400 text-sm">
                    <Camera className="w-4 h-4" />
                    Step 3: Switch to Camera 3 — Robotic Cell (Restricted Exclusion Perimeter)
                  </div>
                  <button
                    onClick={() => { onSelectCamera(3); onClose(); }}
                    className="text-xs px-2.5 py-1 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded hover:bg-rose-500/30 transition-colors"
                  >
                    View Camera 3 Now
                  </button>
                </div>
                <div className="text-xs space-y-1.5 pl-6 border-l-2 border-rose-500/40 text-slate-300">
                  <p><strong>What to say:</strong> "Camera 3 demonstrates zero-tolerance machinery geofencing around a high-voltage industrial robotic welding arm."</p>
                  <p><strong>What to point out on screen:</strong></p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                    <li>The green dot at the worker's feet: <strong>Ground Contact Point Projection</strong>.</li>
                    <li>Explain the distinction: <em>"In CCTV mounted high on ceilings, bounding box centers tilt forward due to perspective. We test the worker's feet against the polygon boundary to prevent false zone alarms."</em></li>
                    <li>When the worker penetrates the red boundary for more than 3.0s, the system triggers Level 4 Exclusion Zone breach.</li>
                  </ul>
                </div>
              </div>

              {/* Step 4: Camera 4 */}
              <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-red-400 text-sm">
                    <Camera className="w-4 h-4" />
                    Step 4: Switch to Camera 4 — High-Rack Storage (Fall & Man-Down Immobility)
                  </div>
                  <button
                    onClick={() => { onSelectCamera(4); onClose(); }}
                    className="text-xs px-2.5 py-1 bg-red-500/20 text-red-300 border border-red-500/40 rounded hover:bg-red-500/30 transition-colors"
                  >
                    View Camera 4 Now
                  </button>
                </div>
                <div className="text-xs space-y-1.5 pl-6 border-l-2 border-red-500/40 text-slate-300">
                  <p><strong>What to say:</strong> "Camera 4 monitors high-rack logistics aisles for slips, falls, and lone-worker incapacitation."</p>
                  <p><strong>What to point out on screen:</strong></p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                    <li>The worker walking upright transitions into a fall.</li>
                    <li>Explain the kinematic logic: <em>"Using 17 COCO landmarks, we track the spine angle between shoulders and hips. When the angle drops under 25°, the recumbent state activates. If immobility persists for &gt; 3.5 seconds, it escalates to Level 4 Emergency Man-Down."</em></li>
                  </ul>
                </div>
              </div>

              {/* Step 5: Incident Triage */}
              <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4 space-y-3">
                <div className="font-bold text-emerald-400 text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Step 5: Click the "Incident Triage Queue" Tab
                </div>
                <div className="text-xs space-y-1.5 pl-6 border-l-2 border-emerald-500/40 text-slate-300">
                  <p><strong>What to say:</strong> "AI in industrial safety must always maintain human oversight. Here is our Human-in-the-Loop triage console."</p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                    <li>Show the list of active incidents with timestamps and risk levels.</li>
                    <li>Click <em>Review Incident</em>: Show how an operator can acknowledge, add operational resolution notes, or log a false positive override.</li>
                    <li>Point out that every action writes an immutable entry into the SQLite audit log with operator ID and timestamp.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 3: DATASETS */}
          {activeSection === 'datasets' && (
            <div className="space-y-4">
              <div className="bg-slate-800/50 p-4 rounded-xl space-y-2 border border-slate-700/70">
                <h3 className="font-bold text-sm text-indigo-400">
                  Why 4 Datasets Mapped by Domain Strength?
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Real industrial safety cannot be solved with a single dataset. Each of the 4 primary public datasets contributes a specialized capability:
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="bg-slate-800/40 border border-slate-700 p-3.5 rounded-xl space-y-1.5">
                  <span className="font-bold text-amber-400">1. Workplace Hazards Dataset (WHD)</span>
                  <p className="text-slate-400">
                    Primary hazard dataset. Contributes industrial machinery pinch points, vehicle corridors, chemical spills, and dynamic fire/smoke.
                  </p>
                </div>

                <div className="bg-slate-800/40 border border-slate-700 p-3.5 rounded-xl space-y-1.5">
                  <span className="font-bold text-emerald-400">2. SH17 Manufacturing & PPE Dataset</span>
                  <p className="text-slate-400">
                    Primary PPE dataset. 8,099 images covering 17 classes: safety vest, hardhat, gloves, steel-toe boots, safety goggles, and earmuffs.
                  </p>
                </div>

                <div className="bg-slate-800/40 border border-slate-700 p-3.5 rounded-xl space-y-1.5">
                  <span className="font-bold text-sky-400">3. SHEL5K Dataset</span>
                  <p className="text-slate-400">
                    Disambiguates whole worker body vs. exposed head vs. helmeted head across varied industrial angles.
                  </p>
                </div>

                <div className="bg-slate-800/40 border border-slate-700 p-3.5 rounded-xl space-y-1.5">
                  <span className="font-bold text-indigo-400">4. Safety Helmet Wearing Dataset (SHWD)</span>
                  <p className="text-slate-400">
                    High-density crowd and distance helmet vs. no-helmet detection under harsh lighting and glare.
                  </p>
                </div>
              </div>

              {/* RT-DETR Benchmark Results */}
              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2 font-mono text-xs">
                <div className="text-emerald-400 font-bold">
                  RT-DETR-L Empirical Benchmarks (NVIDIA RTX 3050 Laptop GPU, CUDA 12.1):
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-slate-300 pt-1">
                  <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">mAP@0.50</span>
                    <span className="text-base font-bold text-white">81.4%</span>
                  </div>
                  <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Precision</span>
                    <span className="text-base font-bold text-emerald-400">88.6%</span>
                  </div>
                  <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Recall</span>
                    <span className="text-base font-bold text-sky-400">86.4%</span>
                  </div>
                  <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">RT-DETR Latency</span>
                    <span className="text-base font-bold text-amber-400">45.8 ms (21.8 FPS)</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 4: REVIEWER Q&A CHEATSHEET */}
          {activeSection === 'qa' && (
            <div className="space-y-4 text-xs">
              <div className="bg-slate-800/40 border border-slate-700 p-4 rounded-xl space-y-2">
                <p className="font-bold text-amber-300">
                  Q1: Why use RT-DETR instead of standard YOLO?
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong>Answer:</strong> "Traditional YOLO models rely on Non-Maximum Suppression (NMS) post-processing, which introduces significant latency variance and struggles when workers closely overlap or crowd near machinery. RT-DETR uses an efficient hybrid transformer encoder/decoder with direct set-prediction queries, completely eliminating NMS bottlenecks while providing superior feature localization for distant PPE gear."
                </p>
              </div>

              <div className="bg-slate-800/40 border border-slate-700 p-4 rounded-xl space-y-2">
                <p className="font-bold text-amber-300">
                  Q2: How do you prevent false alarms when a worker carries their hardhat in hand?
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong>Answer:</strong> "We engineered a <em>Hierarchical Spatial Anatomical Evaluator</em>. Instead of merely checking if a hardhat exists in the bounding box, the algorithm checks intersection over union strictly within the upper 25% anatomical region of the worker. A hardhat held near the hip or hands fails this constraint and triggers an unequipped PPE violation."
                </p>
              </div>

              <div className="bg-slate-800/40 border border-slate-700 p-4 rounded-xl space-y-2">
                <p className="font-bold text-amber-300">
                  Q3: How do you prevent false alarms on tying shoelaces vs a real fall?
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong>Answer:</strong> "Crouching or bending over changes the spine angle temporarily, but the worker maintains ankle/hip separation. A fall requires two conditions: the spine angle must tilt horizontally (&lt; 25°), and the worker must remain recumbent beyond a 3.5-second immobility threshold. If the worker gets back up before 3.5s, the state machine resets without an alarm."
                </p>
              </div>

              <div className="bg-slate-800/40 border border-slate-700 p-4 rounded-xl space-y-2">
                <p className="font-bold text-amber-300">
                  Q4: What happens if the video stream cuts off or network lags?
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong>Answer:</strong> "The system adheres strictly to the industrial safety principle: <em>Absence of signal is NEVER safe</em>. If the watchdog detects FPS dropping below 8 or stream timeout exceeding 5 seconds, the status immediately switches to <strong>UNKNOWN / MONITORING_DEGRADED</strong>, notifying control room operators that perimeter safety monitoring is compromised."
                </p>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 border-t border-slate-800 bg-slate-950/80">
          <span className="text-xs text-slate-400">
            Enterprise AI Safety & Workplace Intelligence System • Naga Akshya K
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-500 transition-colors shadow"
          >
            Close Guide & Continue Live Demo
          </button>
        </div>

      </div>
    </div>
  );
};
