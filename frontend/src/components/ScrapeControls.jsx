import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, RefreshCw, BarChart, FileText } from 'lucide-react';
import { cn } from '../lib/utils';

export function ScrapeControls({ onScrapeComplete }) {
    const [loading, setLoading] = useState({ t212: false, yfinance: false });
    const [status, setStatus] = useState(null);

    const handleScrape = async (type) => {
        setLoading(prev => ({ ...prev, [type]: true }));
        setStatus(`Scraping ${type === 't212' ? 'Trading212' : 'Yahoo Finance'}...`);

        try {
            const response = await axios.post(`http://127.0.0.1:8000/scrape/${type}`);
            setStatus(`Success: ${response.data.status || 'Completed'}`);
            if (onScrapeComplete) onScrapeComplete();
        } catch (error) {
            console.error(error);
            setStatus(`Error: ${error.response?.data?.detail || error.message}`);
        } finally {
            setLoading(prev => ({ ...prev, [type]: false }));
            // Clear status after 3 seconds
            setTimeout(() => setStatus(null), 3000);
        }
    };

    return (
        <div className="bg-card text-card-foreground p-6 rounded-lg border shadow-sm">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <RefreshCw className="w-5 h-5" />
                Scrape Controls
            </h2>

            <div className="flex flex-col sm:flex-row gap-4 mb-4">
                <button
                    onClick={() => handleScrape('t212')}
                    disabled={loading.t212 || loading.yfinance}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-md font-medium transition-all duration-200",
                        "bg-primary text-primary-foreground hover:bg-primary/90",
                        "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                >
                    {loading.t212 ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                    Scrape Trading212
                </button>

                <button
                    onClick={() => handleScrape('yfinance')}
                    disabled={loading.t212 || loading.yfinance}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-md font-medium transition-all duration-200",
                        "bg-secondary text-secondary-foreground hover:bg-secondary/80",
                        "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                >
                    {loading.yfinance ? <Loader2 className="w-4 h-4 animate-spin" /> : <BarChart className="w-4 h-4" />}
                    Scrape Yahoo Finance
                </button>
            </div>

            {status && (
                <div className={cn(
                    "p-3 rounded-md text-sm font-medium animate-in fade-in slide-in-from-top-1",
                    status.startsWith('Error')
                        ? "bg-destructive/10 text-destructive"
                        : "bg-green-500/10 text-green-500"
                )}>
                    {status}
                </div>
            )}
        </div>
    );
}
