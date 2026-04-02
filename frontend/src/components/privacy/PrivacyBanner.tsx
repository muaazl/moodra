'use client';

import React from 'react';
import { Lock, Cpu, EyeOff, ZapOff } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card"

export const PrivacyBanner = () => {
  const steps = [
    {
      icon: <Cpu className="w-5 h-5 text-zinc-400" />,
      title: "100% Local Processing",
      description: "Everything runs on your machine. Your chats never touch our servers or the cloud."
    },
    {
      icon: <ZapOff className="w-5 h-5 text-zinc-400" />,
      title: "Zero Data Retention",
      description: "We don't have a database. Close the tab, and every line of your chat is gone forever."
    },
    {
      icon: <EyeOff className="w-5 h-5 text-zinc-400" />,
      title: "Anonymous Usage",
      description: "No login. No tracking. No cookies that follow you around. Just pure analysis."
    }
  ];

  return (
    <section className="py-12 px-6 bg-zinc-500/5 border-y border-zinc-500/10 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-zinc-500/15 border border-zinc-500/30 text-zinc-300 text-sm font-semibold mb-4 tracking-wide shadow-none">
            <Lock className="w-4 h-4 fill-zinc-500/20" />
            <span>Built with Privacy by Design</span>
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight mb-4">
            Analysis That Respects Your Secrets
          </h2>
          <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
            We designed "Expose The Chat" to be the most private way to see what's really happening in your conversations. 
            No logins, no cloud, no BS. Just your data, your insights, your control.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {steps.map((step, idx) => (
            <Card key={idx} className="bg-zinc-950/40 border-zinc-900 group transition-all duration-300 hover:border-zinc-500/40 hover:shadow-2xl hover:shadow-zinc-500/10">
              <CardContent className="p-8">
                <div className="mb-6 p-3 rounded-2xl bg-zinc-500/10 w-fit transition-transform group-hover:scale-110 group-hover:shadow-none">
                  {step.icon}
                </div>
                <h3 className="text-xl font-bold text-zinc-100 mb-3 group-hover:text-zinc-400 transition-colors">
                  {step.title}
                </h3>
                <p className="text-zinc-400 leading-relaxed text-sm">
                  {step.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
