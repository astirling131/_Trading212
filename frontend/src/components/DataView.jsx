import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, FileSpreadsheet, ChevronRight, ChevronLeft } from 'lucide-react';

export function DataView({ type, refreshTrigger }) {
    const [fileList, setFileList] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContent, setFileContent] = useState(null);
    const [loading, setLoading] = useState(false);
    const [contentLoading, setContentLoading] = useState(false);

    // Fetch list of files
    useEffect(() => {
        const fetchFiles = async () => {
            setLoading(true);
            try {
                const endpoint = type === 'reports' ? '/data/reports' : '/data/market';
                const res = await axios.get(`http://127.0.0.1:8000${endpoint}`); // Explicit IP to avoid localhost issues
                const files = res.data.reports || res.data.files;
                setFileList(files);
            } catch (err) {
                console.error("Failed to fetch files", err);
            } finally {
                setLoading(false);
            }
        };
        fetchFiles();
    }, [type, refreshTrigger]);

    // Fetch file content when selected
    useEffect(() => {
        if (!selectedFile) {
            setFileContent(null);
            return;
        }

        const fetchContent = async () => {
            setContentLoading(true);
            try {
                const res = await axios.get(`http://127.0.0.1:8000/data/content?path=${encodeURIComponent(selectedFile)}`);
                setFileContent(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setContentLoading(false);
            }
        }
        fetchContent();
    }, [selectedFile]);

    return (
        <div className="bg-card text-card-foreground rounded-lg border shadow-sm flex flex-col h-[600px] overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between bg-muted/30">
                <h3 className="font-semibold flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4" />
                    {type === 'reports' ? 'History Reports' : 'Market Data'}
                </h3>
                <span className="text-xs text-muted-foreground">{fileList.length} files found</span>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar: File List */}
                <div className="w-1/3 border-r overflow-y-auto bg-muted/10">
                    {loading ? (
                        <div className="flex justify-center p-4"><Loader2 className="animate-spin text-muted-foreground" /></div>
                    ) : (
                        <ul className="divide-y divide-border/50">
                            {fileList.map((file) => (
                                <li
                                    key={file}
                                    onClick={() => setSelectedFile(file)}
                                    className={`p-3 text-sm cursor-pointer hover:bg-muted transition-colors truncate ${selectedFile === file ? 'bg-muted font-medium' : ''}`}
                                    title={file}
                                >
                                    {file.replace('market_data\\', '').replace('market_data/', '')}
                                </li>
                            ))}
                            {fileList.length === 0 && <li className="p-4 text-sm text-muted-foreground text-center">No files found</li>}
                        </ul>
                    )}
                </div>

                {/* Main: File Content */}
                <div className="w-2/3 overflow-auto p-4 bg-background">
                    {contentLoading ? (
                        <div className="flex justify-center items-center h-full text-muted-foreground">
                            <Loader2 className="w-8 h-8 animate-spin mb-2" />
                        </div>
                    ) : fileContent ? (
                        <div>
                            <h4 className="font-medium mb-2 sticky top-0 bg-background pb-2 border-b">{fileContent.filename}</h4>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm border-collapse text-left">
                                    <thead className="text-xs uppercase bg-muted text-muted-foreground sticky top-8">
                                        <tr>
                                            {fileContent.columns.map(col => (
                                                <th key={col} className="px-3 py-2 font-medium border-b">{col}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border/50">
                                        {fileContent.data.slice(0, 100).map((row, i) => (
                                            <tr key={i} className="hover:bg-muted/50">
                                                {fileContent.columns.map(col => (
                                                    <td key={col} className="px-3 py-2 whitespace-nowrap">{String(row[col])}</td>
                                                ))}
                                            </tr>
                                        ))}
                                        {fileContent.data.length > 100 && (
                                            <tr>
                                                <td colSpan={fileContent.columns.length} className="px-3 py-2 text-center text-muted-foreground italic">
                                                    ... {fileContent.data.length - 100} more rows ...
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                            <ChevronLeft className="w-8 h-8 mb-2 opacity-20" />
                            <p>Select a file to view content</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
