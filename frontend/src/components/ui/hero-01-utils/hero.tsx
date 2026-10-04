import React from "react";
import { ArrowRight, Play, Star, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface AvatarList {
  image: string;
}

interface HeroSectionProps {
  avatarList: AvatarList[];
}

export default function HeroSection({ avatarList }: HeroSectionProps) {
  // Reliable Unsplash stock images for fallback
  const fallbackAvatars = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&q=80",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=120&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&q=80",
  ];

  const avatars = (avatarList && avatarList.length > 0) ? avatarList : fallbackAvatars.map(img => ({ image: img }));

  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-16 md:pb-28">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/20 via-purple-600/20 to-pink-500/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10 text-center">
        {/* Top Feature Pill */}
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-6 shadow-sm shadow-indigo-500/10">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span>Next-Generation Audience Intelligence</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            k-Anonymity Verified
          </span>
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.15]">
          Transform Raw Social Streams Into{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
            Real-Time Audience Truth
          </span>
        </h1>

        {/* Subtitle */}
        <p className="mt-5 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Ingest multi-platform social feeds, detect 8-class emotional arcs with Hinglish code-mixing, forecast viral trend bursts, and map information cascades across communities.
        </p>

        {/* Call to Actions */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Button
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30 gap-2 px-6"
          >
            <span>Launch Live Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="lg"
            className="border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-200 font-semibold gap-2 px-6 backdrop-blur"
          >
            <Play className="w-4 h-4 fill-slate-300 text-slate-300" />
            <span>Watch Demo (3 min)</span>
          </Button>
        </div>

        {/* Social Proof & Avatars */}
        <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4 text-xs text-slate-400">
          <div className="flex -space-x-2.5 overflow-hidden p-1">
            {avatars.slice(0, 4).map((av, index) => (
              <img
                key={index}
                src={av.image}
                alt="Analyst user avatar"
                className="inline-block h-8 w-8 rounded-full ring-2 ring-slate-950 object-cover"
                onError={(e) => {
                  e.currentTarget.src = fallbackAvatars[index % fallbackAvatars.length];
                }}
              />
            ))}
          </div>

          <div className="flex items-center space-x-1.5">
            <div className="flex text-amber-400">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              ))}
            </div>
            <span className="font-semibold text-slate-200">5.0</span>
            <span>· Trusted by 12,000+ data science & policy teams</span>
          </div>
        </div>
      </div>
    </section>
  );
}
