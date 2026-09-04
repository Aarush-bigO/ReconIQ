"use client";
import { useRef, useEffect, useCallback } from "react";

/* ── Animated Reconciliation Flow SVG ─────────────────────── */
export default function LandingHero() {
  return (
    <div className="hero-visual">
      <svg viewBox="0 0 480 480" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: "100%", height: "100%" }}>
        {/* Background grid pattern */}
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0,0,0,0.03)" strokeWidth="1" />
          </pattern>
          <linearGradient id="flowGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0037ff" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#00d67d" stopOpacity="0.6" />
          </linearGradient>
          <linearGradient id="flowGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#305eff" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#3dffae" stopOpacity="0.4" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="softShadow">
            <feDropShadow dx="0" dy="4" stdDeviation="8" floodColor="#000" floodOpacity="0.06" />
          </filter>
        </defs>

        <rect width="480" height="480" fill="url(#grid)" />

        {/* ── Source Nodes (Left side) ── */}
        {/* Razorpay Node */}
        <g className="node-animate" style={{ transformOrigin: "80px 120px" }}>
          <rect x="30" y="85" width="100" height="70" rx="16" fill="white" stroke="#e5e5e5" strokeWidth="1.5" filter="url(#softShadow)" />
          <rect x="42" y="97" width="32" height="6" rx="3" fill="#0037ff" opacity="0.8" />
          <text x="80" y="125" textAnchor="middle" fontSize="10" fontWeight="700" fill="#333">Razorpay</text>
          <rect x="50" y="133" width="60" height="4" rx="2" fill="#e5e5e5" />
          <rect x="55" y="141" width="50" height="4" rx="2" fill="#f0f0f0" />
        </g>

        {/* Bank Node */}
        <g className="node-animate" style={{ transformOrigin: "80px 240px", animationDelay: "0.3s" }}>
          <rect x="30" y="205" width="100" height="70" rx="16" fill="white" stroke="#e5e5e5" strokeWidth="1.5" filter="url(#softShadow)" />
          <rect x="42" y="217" width="32" height="6" rx="3" fill="#22c55e" opacity="0.8" />
          <text x="80" y="245" textAnchor="middle" fontSize="10" fontWeight="700" fill="#333">Bank</text>
          <rect x="50" y="253" width="60" height="4" rx="2" fill="#e5e5e5" />
          <rect x="55" y="261" width="50" height="4" rx="2" fill="#f0f0f0" />
        </g>

        {/* Ledger Node */}
        <g className="node-animate" style={{ transformOrigin: "80px 360px", animationDelay: "0.6s" }}>
          <rect x="30" y="325" width="100" height="70" rx="16" fill="white" stroke="#e5e5e5" strokeWidth="1.5" filter="url(#softShadow)" />
          <rect x="42" y="337" width="32" height="6" rx="3" fill="#f59e0b" opacity="0.8" />
          <text x="80" y="365" textAnchor="middle" fontSize="10" fontWeight="700" fill="#333">Ledger</text>
          <rect x="50" y="373" width="60" height="4" rx="2" fill="#e5e5e5" />
          <rect x="55" y="381" width="50" height="4" rx="2" fill="#f0f0f0" />
        </g>

        {/* ── Flow Lines (animated) ── */}
        <path d="M130 120 C180 120, 190 240, 220 240" stroke="url(#flowGrad2)" strokeWidth="2" fill="none" className="flow-line" />
        <path d="M130 240 L220 240" stroke="url(#flowGrad2)" strokeWidth="2" fill="none" className="flow-line flow-line-delay-1" />
        <path d="M130 360 C180 360, 190 240, 220 240" stroke="url(#flowGrad2)" strokeWidth="2" fill="none" className="flow-line flow-line-delay-2" />

        {/* ── Central Engine ── */}
        <g className="node-animate" style={{ transformOrigin: "280px 240px", animationDelay: "0.4s" }}>
          <rect x="220" y="190" width="120" height="100" rx="20" fill="white" stroke="#0037ff" strokeWidth="2" filter="url(#softShadow)" />
          {/* Icon */}
          <circle cx="280" cy="225" r="16" fill="#f0f3fe" />
          <path d="M273 225L278 230L288 220" stroke="#0037ff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          <text x="280" y="260" textAnchor="middle" fontSize="10" fontWeight="700" fill="#0037ff">ReconIQ</text>
          <text x="280" y="274" textAnchor="middle" fontSize="8" fontWeight="500" fill="#9e9e9e">AI Engine</text>
        </g>

        {/* ── Output Flow Lines ── */}
        <path d="M340 230 L390 180" stroke="url(#flowGrad1)" strokeWidth="2" fill="none" className="flow-line flow-line-delay-2" filter="url(#glow)" />
        <path d="M340 240 L390 240" stroke="url(#flowGrad1)" strokeWidth="2" fill="none" className="flow-line flow-line-delay-3" filter="url(#glow)" />
        <path d="M340 250 L390 300" stroke="url(#flowGrad1)" strokeWidth="2" fill="none" className="flow-line flow-line-delay-1" filter="url(#glow)" />

        {/* ── Result Nodes (Right side) ── */}
        {/* Matched */}
        <g className="node-animate" style={{ transformOrigin: "430px 180px", animationDelay: "0.8s" }}>
          <rect x="390" y="155" width="80" height="50" rx="12" fill="#f0fdf4" stroke="#bbf7d0" strokeWidth="1.5" />
          <circle cx="408" cy="175" r="6" fill="#22c55e" />
          <path d="M405 175L407 177L411 173" stroke="white" strokeWidth="1.5" strokeLinecap="round" fill="none" />
          <text x="435" y="179" textAnchor="middle" fontSize="9" fontWeight="600" fill="#16a34a">Matched</text>
        </g>

        {/* Review */}
        <g className="node-animate" style={{ transformOrigin: "430px 240px", animationDelay: "1s" }}>
          <rect x="390" y="215" width="80" height="50" rx="12" fill="#fffbeb" stroke="#fde68a" strokeWidth="1.5" />
          <circle cx="408" cy="235" r="6" fill="#f59e0b" />
          <text x="406" y="239" textAnchor="middle" fontSize="7" fontWeight="700" fill="white">!</text>
          <text x="438" y="239" textAnchor="middle" fontSize="9" fontWeight="600" fill="#d97706">Review</text>
        </g>

        {/* Audit */}
        <g className="node-animate" style={{ transformOrigin: "430px 300px", animationDelay: "1.2s" }}>
          <rect x="390" y="275" width="80" height="50" rx="12" fill="#f0f3fe" stroke="#bbc9fb" strokeWidth="1.5" />
          <circle cx="408" cy="295" r="6" fill="#0037ff" />
          <path d="M405 295L407 297L411 293" stroke="white" strokeWidth="1.5" strokeLinecap="round" fill="none" />
          <text x="440" y="299" textAnchor="middle" fontSize="9" fontWeight="600" fill="#0037ff">Audited</text>
        </g>

        {/* ── Floating data particles ── */}
        <circle cx="170" cy="140" r="3" fill="#0037ff" opacity="0.2">
          <animate attributeName="cy" values="140;130;140" dur="3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0.5;0.2" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx="185" cy="280" r="2" fill="#00d67d" opacity="0.3">
          <animate attributeName="cy" values="280;270;280" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="360" cy="200" r="2.5" fill="#0037ff" opacity="0.2">
          <animate attributeName="cx" values="360;370;360" dur="3.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="175" cy="330" r="2" fill="#f59e0b" opacity="0.25">
          <animate attributeName="cy" values="330;320;330" dur="3.2s" repeatCount="indefinite" />
        </circle>

        {/* ── Accuracy label ── */}
        <g>
          <rect x="236" y="386" width="88" height="36" rx="10" fill="white" stroke="#e5e5e5" strokeWidth="1" filter="url(#softShadow)" />
          <text x="280" y="400" textAnchor="middle" fontSize="8" fontWeight="500" fill="#9e9e9e">Accuracy</text>
          <text x="280" y="414" textAnchor="middle" fontSize="12" fontWeight="800" fill="#22c55e">99.7%</text>
        </g>

        {/* Processing time label */}
        <g>
          <rect x="236" y="430" width="88" height="36" rx="10" fill="white" stroke="#e5e5e5" strokeWidth="1" filter="url(#softShadow)" />
          <text x="280" y="444" textAnchor="middle" fontSize="8" fontWeight="500" fill="#9e9e9e">Latency</text>
          <text x="280" y="458" textAnchor="middle" fontSize="12" fontWeight="800" fill="#0037ff">&lt; 1 sec</text>
        </g>
      </svg>
    </div>
  );
}
