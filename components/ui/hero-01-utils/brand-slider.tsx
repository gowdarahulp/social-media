import React from "react";
import { Cpu, Globe, Layers, Shield, Zap } from "lucide-react";

export interface BrandList {
  image: string;
  lightimg?: string;
  name: string;
}

interface BrandSliderProps {
  brandList: BrandList[];
}

export default function BrandSlider({ brandList }: BrandSliderProps) {
  const fallbackIcons = [Zap, Cpu, Globe, Layers, Shield];

  return (
    <section className="py-12 border-y border-slate-900 bg-slate-950/60 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
        <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-6">
          Powering audience intelligence for modern tech leaders & research labs
        </p>

        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12 opacity-75">
          {brandList.map((brand, i) => {
            const Icon = fallbackIcons[i % fallbackIcons.length];
            return (
              <div
                key={brand.name + i}
                className="flex items-center space-x-2 grayscale hover:grayscale-0 transition-all duration-300 opacity-60 hover:opacity-100 group"
              >
                <img
                  src={brand.image}
                  alt={brand.name}
                  className="h-6 w-auto object-contain hidden sm:block"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />
                <div className="flex items-center space-x-1.5 text-slate-400 group-hover:text-indigo-400 transition-colors">
                  <Icon className="w-5 h-5 text-indigo-400/80" />
                  <span className="text-xs font-bold tracking-tight text-slate-300">
                    {brand.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
