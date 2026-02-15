import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2 } from 'lucide-react';

export function MainContent({ activeView }) {
    // Simple view routing
    const renderView = () => {
        if (activeView.startsWith('ticker:')) {
            const ticker = activeView.split(':')[1];
            return <TickerView ticker={ticker} />;
        }

        switch (activeView) {
            case 'overview': return <PlaceholderView title="Overview" />;
            case 'history': return <PlaceholderView title="History" />;
            case 'analysis': return <PlaceholderView title="Analysis" />;
            case 'orders': return <PlaceholderView title="Orders" />;
            default: return <PlaceholderView title="Select a View" />;
        }
    };

    return (
        <main className="flex-1 bg-surface m-4 rounded-xl border border-border overflow-hidden relative shadow-inner">
            {/* Inner shadow/gradient overlay for depth */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

            <div className="h-full overflow-auto p-6 relative z-10">
                {renderView()}
            </div>
        </main>
    );
}

function PlaceholderView({ title }) {
    return (
        <div className="flex flex-col items-center justify-center h-full text-text-muted">
            <h2 className="text-3xl font-bold mb-4 opacity-50">{title}</h2>
            <p>Content for {title} will appear here.</p>
        </div>
    );
}

function TickerView({ ticker }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                // Construct path to expected file
                // Note: In a real app we might ask API for data directly, but here we read the CSV generated
                // We'll search for the file via the content API we built earlier
                const path = `market_data/${ticker}.L_15m.csv`; // Try with .L first as per script logic
                // Or just list files and find match. For now, let's try direct path assuming script naming

                // Actually, let's use the list API to find the file first to be safe
                const listRes = await axios.get('http://127.0.0.1:8000/data/market');
                const files = listRes.data.files;
                const match = files.find(f => f.includes(ticker));

                if (match) {
                    const contentRes = await axios.get(`http://127.0.0.1:8000/data/content?path=${encodeURIComponent(match)}`);
                    setData(contentRes.data);
                } else {
                    setError("No data found. Ensure you are connected/scraped.");
                }

            } catch (err) {
                console.error(err);
                setError("Failed to load ticker data");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [ticker]);

    if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
    if (error) return <div className="flex items-center justify-center h-full text-danger">{error}</div>;
    if (!data) return <div className="flex items-center justify-center h-full text-text-muted">No data available</div>;

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white border-b border-border pb-2">{ticker} Market Data</h2>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-text-muted uppercase bg-black/20">
                        <tr>
                            {data.columns.map(col => <th key={col} className="px-4 py-3">{col}</th>)}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30 text-text-main">
                        {data.data.slice(0, 50).map((row, i) => (
                            <tr key={i} className="hover:bg-white/5">
                                {data.columns.map(col => <td key={col} className="px-4 py-2 whitespace-nowrap">{row[col]}</td>)}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
