import React from 'react';
import { cn } from '../lib/utils';
import { Loader2 } from 'lucide-react';

export function TopBar({ status, balance, onConnect, onDisconnect, isLoading }) {

    const isConnected = status === 'connected';

    return (
        <header className="h-20 border-b border-border bg-background flex items-center justify-between px-6 shrink-0">

            {/* Left Actions: Get Data Buttons */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onConnect}
                    disabled={isLoading}
                    className={cn(
                        "px-6 py-2 rounded-md font-bold transition-all duration-200 min-w-[120px]",
                        "bg-[#007acc] hover:bg-[#006bb3] text-white shadow-lg", // Specific blue tone
                        "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                >
                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : "Get Trading212 Info"}
                </button>

                <button
                    onClick={onDisconnect}
                    disabled={isLoading}
                    className={cn(
                        "px-6 py-2 rounded-md font-bold transition-all duration-200 min-w-[120px]",
                        "bg-[#007acc] hover:bg-[#006bb3] text-white shadow-lg",
                        "disabled:opacity-50 disabled:cursor-not-allowed"
                    )}
                >
                    Get Stock Info
                </button>
            </div>

            {/* Right Status Indicators */}
            <div className="flex items-center gap-4">
                {/* Balance Pill */}
                <div className="bg-surface border border-border px-6 py-2 rounded-md text-text-muted font-medium min-w-[180px] text-center shadow-md">
                    Balance: {balance !== null ? `£${balance.toLocaleString()}` : ''}
                </div>

                {/* Return Pill */}
                <div className="bg-surface border border-border px-6 py-2 rounded-md text-text-muted font-medium min-w-[160px] text-center shadow-md">
                    Return: {isConnected ? '182%' : ''}
                </div>

                {/* Status Pill */}
                <div className={cn(
                    "px-6 py-2 rounded-md font-bold text-white min-w-[180px] text-center shadow-md transition-colors duration-300",
                    isConnected ? "bg-[#2ea043]" : "bg-[#da3633]" // Github-like Green/Red
                )}>
                    Status: {isConnected ? 'Connected' : 'Disconnected'}
                </div>
            </div>
        </header>
    );
}
