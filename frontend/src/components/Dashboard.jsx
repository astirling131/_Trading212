import React, { useState } from 'react';
import { ScrapeControls } from './ScrapeControls';
import { DataView } from './DataView';
import { LayoutDashboard, TrendingUp } from 'lucide-react';

export function Dashboard() {
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleScrapeComplete = () => {
        // Increment trigger to refresh file lists
        setRefreshTrigger(prev => prev + 1);
    };

    return (
        <div className="container mx-auto p-6 max-w-7xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
                        <span className="p-2 bg-primary/10 rounded-lg text-primary">
                            <LayoutDashboard className="w-8 h-8" />
                        </span>
                        Trading212 Data Scraper
                    </h1>
                    <p className="text-muted-foreground ml-14">
                        Manage your market data and account history reports.
                    </p>
                </div>
                <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground bg-muted/30 px-4 py-2 rounded-full border">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span>System Ready</span>
                </div>
            </header>

            <div className="grid gap-6">
                <section>
                    <ScrapeControls onScrapeComplete={handleScrapeComplete} />
                </section>

                <section className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                        <h2 className="text-lg font-semibold tracking-tight">Recent Scrapes</h2>
                        <DataView type="reports" refreshTrigger={refreshTrigger} />
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-lg font-semibold tracking-tight">Market Data</h2>
                        <DataView type="market" refreshTrigger={refreshTrigger} />
                    </div>
                </section>
            </div>
        </div>
    );
}
