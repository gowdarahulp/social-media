import React, { useState } from "react";
import { Activity, Menu, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";

export interface NavigationSection {
  title: string;
  href: string;
  isActive?: boolean;
}

interface HeaderProps {
  navigationData: NavigationSection[];
}

export default function Header({ navigationData }: HeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <a href="#" className="flex flex-col">
            <span className="text-lg font-bold tracking-tight text-white">SocialPulse</span>
            <span className="text-[10px] text-slate-400 font-medium -mt-1">Audience IQ</span>
          </a>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-1">
          <NavigationMenu>
            <NavigationMenuList className="space-x-1">
              {navigationData.map((item) => (
                <NavigationMenuItem key={item.title}>
                  <NavigationMenuLink
                    href={item.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                      item.isActive
                        ? "bg-slate-800 text-white"
                        : "text-slate-400 hover:text-white hover:bg-slate-900"
                    }`}
                  >
                    {item.title}
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        {/* Header Right Actions */}
        <div className="hidden sm:flex items-center space-x-3">
          <div className="relative w-40 lg:w-48">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <Input
              type="text"
              placeholder="Search topics..."
              className="h-8 pl-8 pr-3 text-xs bg-slate-900 border-slate-800 text-slate-200 placeholder:text-slate-500 rounded-lg focus-visible:ring-indigo-500"
            />
          </div>

          <Button
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm"
          >
            Get Started
          </Button>
        </div>

        {/* Mobile Hamburger Menu */}
        <div className="flex sm:hidden">
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="text-slate-300">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-slate-950 border-slate-800 text-slate-100 p-6">
              <SheetHeader>
                <SheetTitle className="text-white text-left font-bold flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-indigo-400" />
                  <span>SocialPulse</span>
                </SheetTitle>
              </SheetHeader>
              <div className="mt-6 flex flex-col space-y-3">
                {navigationData.map((item) => (
                  <a
                    key={item.title}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`py-2 px-3 rounded-lg text-sm font-medium ${
                      item.isActive
                        ? "bg-indigo-600/20 text-indigo-400"
                        : "text-slate-400 hover:text-white hover:bg-slate-900"
                    }`}
                  >
                    {item.title}
                  </a>
                ))}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
