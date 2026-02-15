import React from 'react';
import { LayoutGrid, History, LineChart, FileText, Settings, PiggyBank, Menu, LogOut } from 'lucide-react';
import { cn } from '../lib/utils';

export function Sidebar({ activeView, setActiveView }) {

    const navItems = [
        { id: 'overview', label: 'Overview', icon: LayoutGrid },
        { id: 'history', label: 'History', icon: History },
        { id: 'analysis', label: 'Analysis', icon: LineChart },
        { id: 'orders', label: 'Orders', icon: FileText },
    ];

    const tickers = [
        'CSP1', 'VHYL', 'INFR',
        'IGL5', 'XMWX', '',
        '', '', ''
    ];

    return (
        <aside className="w-64 bg-background flex flex-col border-r border-border h-full">
            {/* Header / Logo Area */}
            <div className="p-4 flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-black">
                    <PiggyBank className="w-7 h-7" />
                </div>
                <div className="bg-white px-4 py-2 rounded-lg font-bold text-black flex-1 text-center">
                    Investments
                </div>
            </div>

            {/* Menu Icon */}
            <div className="px-4 mb-4">
                <Menu className="w-8 h-8 text-text-muted cursor-pointer hover:text-white transition-colors" />
            </div>

            {/* Main Navigation */}
            <div className="px-3 flex flex-col gap-2 mb-6">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveView(item.id)}
                        className={cn(
                            "w-full py-3 px-4 rounded-lg font-medium text-left transition-all duration-200 border border-transparent",
                            activeView === item.id
                                ? "bg-surface border-border shadow-sm text-white"
                                : "bg-transparent text-text-muted hover:bg-surface/50 hover:text-white"
                        )}
                    >
                        {item.label}
                    </button>
                ))}
            </div>

            {/* Tickers Grid */}
            <div className="px-3">
                <h3 className="text-text-muted text-center mb-2 font-medium">Tickers</h3>
                <div className="grid grid-cols-3 gap-2 bg-black/20 p-2 rounded-xl">
                    {tickers.map((ticker, idx) => (
                        <button
                            key={idx}
                            disabled={!ticker}
                            onClick={() => ticker && setActiveView(`ticker:${ticker}`)}
                            className={cn(
                                "aspect-square rounded-md flex items-center justify-center text-sm font-medium transition-all duration-200",
                                ticker
                                    ? "bg-surface hover:bg-border text-text-muted hover:text-white border border-border"
                                    : "bg-transparent border border-border/30 opacity-50 cursor-default",
                                activeView === `ticker:${ticker}` && "bg-border text-white border-primary/50 ring-1 ring-primary/50"
                            )}
                        >
                            {ticker}
                        </button>
                    ))}
                </div>
            </div>

            {/* Footer Settings */}
            <div className="mt-auto p-4">
                <div className="flex items-center gap-2">
                    <button className="flex items-center gap-2 text-text-muted hover:text-white transition-colors text-sm font-medium">
                        <Settings className="w-4 h-4" />
                        Settings
                    </button>

                    <button
                        onClick={async () => {
                            if (confirm("Are you sure you want to exit? This will stop the backend and close the application.")) {
                                try {
                                    // 1. Stop Backend
                                    // We use fetch/axios directly here. Need to import axios if not present, 
                                    // or just use fetch since we don't need complex error handling if it's dying.
                                    await fetch('http://127.0.0.1:8000/shutdown', { method: 'POST' });
                                } catch (e) {
                                    console.error("Shutdown signal failed (maybe already dead):", e);
                                }
                                // 2. Close Window
                                window.close();
                                // Fallback if window.close is blocked
                                document.body.innerHTML = "<div style='display:flex;height:100vh;align-items:center;justify-content:center;color:white;background:#111;'><h1>Application Shutdown. You can close this tab.</h1></div>";
                            }
                        }}
                        className="flex items-center gap-2 text-text-muted hover:text-red-400 transition-colors text-sm font-medium ml-4"
                    >
                        <LogOut className="w-4 h-4" />
                        Exit
                    </button>
                </div>
            </div>
        </aside>
    );
}
