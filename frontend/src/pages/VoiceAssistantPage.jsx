import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const VoiceAssistantPage = () => {
    const navigate = useNavigate();
    const [status, setStatus] = useState('idle'); // idle, listening, processing, speaking
    const [messages, setMessages] = useState([]);
    const [summary, setSummary] = useState({});

    // Refs for speech
    const recognition = useRef(null);
    const synth = useRef(window.speechSynthesis);

    useEffect(() => {
        // Initialize Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognition.current = new SpeechRecognition();
            recognition.current.continuous = false;
            recognition.current.lang = 'en-US'; // Default to English for now, could switch
            recognition.current.interimResults = false;

            recognition.current.onstart = () => setStatus('listening');
            recognition.current.onend = () => {
                if (status === 'listening') {
                    // unexpected end, maybe silence
                    // setStatus('idle'); 
                }
            };

            recognition.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setStatus('processing');
                handleUserMessage(transcript);
            };
        }

        // Initial greeting
        handleAIResponse("Hello! I am your Amt-Assistent. I can help you with your Munich Residence Registration. Shall we start?");

        return () => {
            if (recognition.current) recognition.current.stop();
            if (synth.current) synth.current.cancel();
        };
    }, []);

    const speak = (text) => {
        if (!synth.current) return;
        setStatus('speaking');
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onend = () => {
            setStatus('idle');
            startListening(); // Auto-listen after speaking
        };
        synth.current.speak(utterance);
    };

    const startListening = () => {
        if (recognition.current && status !== 'listening') {
            try {
                recognition.current.start();
            } catch (e) {
                console.error("Already started", e);
            }
        }
    };

    const stopListening = () => {
        if (recognition.current) {
            recognition.current.stop();
            setStatus('idle');
        }
    };

    const toggleListening = () => {
        if (status === 'listening') {
            stopListening();
        } else {
            startListening();
        }
    };

    const handleUserMessage = async (text) => {
        // Add user message to UI
        const newMsg = { sender: 'user', text };
        setMessages(prev => [...prev, newMsg]);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: 'user-session-1' })
            });

            if (!response.ok) {
                let errorMessage = `Error ${response.status}: ${response.statusText}`;
                try {
                    // Try to parse JSON error details from backend
                    const errorJson = await response.json();
                    if (errorJson.detail) {
                        errorMessage = `Server Error: ${errorJson.detail}`;
                    }
                } catch (e) {
                    // Fallback to text if not JSON
                    const errorText = await response.text();
                    if (errorText) errorMessage += ` (${errorText.substring(0, 100)})`;
                }

                console.error(`API Error:`, errorMessage);
                handleAIResponse(`I am sorry, I am having trouble connecting to the server. \n\nDebug Info: ${errorMessage}`);
                return;
            }

            const data = await response.json();
            handleAIResponse(data.response);
        } catch (error) {
            console.error("Network/Parsing Error", error);
            handleAIResponse("I am sorry, I am having trouble connecting to the server.");
        }
    };

    const handleAIResponse = (text) => {
        const newMsg = { sender: 'assistant', text };
        setMessages(prev => [...prev, newMsg]);
        speak(text);
    }

    return (
        <div className="relative flex min-h-screen w-full flex-col overflow-hidden bg-background-light dark:bg-background-dark text-slate-900 dark:text-white transition-colors duration-200">
            {/* Header */}
            <header className="flex items-center justify-between whitespace-nowrap border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-4 lg:px-12 shadow-sm z-20">
                <div className="flex items-center gap-4">
                    <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                        <div className="flex items-center justify-center size-10 rounded-lg bg-primary/10 text-primary">
                            <span className="material-symbols-outlined text-3xl">assistant</span>
                        </div>
                        <h2 className="text-slate-900 dark:text-white text-xl font-bold tracking-tight">Bureaucracy Helper</h2>
                    </Link>
                </div>
                {/* ... (settings buttons intentionally simplified for brevity in this update) ... */}
            </header>

            {/* Main Content Layout */}
            <main className="flex flex-1 flex-col lg:flex-row max-w-[1400px] mx-auto w-full p-6 lg:p-10 gap-8">
                {/* LEFT COLUMN: Voice Interaction Zone */}
                <div className="flex flex-col flex-[2] gap-8 justify-center items-center relative">
                    {/* Status Headline */}
                    <div className="text-center space-y-2 z-10">
                        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full ${status === 'listening' ? 'bg-primary/10 text-primary' : 'bg-slate-200 text-slate-600'} font-bold text-sm mb-2`}>
                            {status === 'listening' && (
                                <span className="relative flex h-3 w-3">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
                                </span>
                            )}
                            {status === 'listening' ? "Active Listening" : status === 'speaking' ? "Speaking..." : "Paused"}
                        </div>
                        <h1 className="text-slate-900 dark:text-white text-4xl md:text-5xl font-bold tracking-tight leading-tight">
                            {status === 'listening' ? "I am listening..." : "I am ready."}
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 text-lg">Speak naturally.</p>
                    </div>

                    {/* Central Visualizer */}
                    <div className="relative flex items-center justify-center py-10">
                        {status === 'listening' && (
                            <>
                                <div className="absolute size-[300px] rounded-full bg-primary/5 dark:bg-primary/10 animate-[ping_3s_linear_infinite]"></div>
                                <div className="absolute size-[240px] rounded-full bg-primary/10 dark:bg-primary/20 animate-[ping_2s_linear_infinite]"></div>
                            </>
                        )}
                        <button
                            onClick={toggleListening}
                            className={`relative size-32 rounded-full shadow-2xl flex items-center justify-center z-10 transition-transform hover:scale-105 duration-300 cursor-pointer group ${status === 'listening' ? 'bg-primary' : 'bg-slate-400'}`}>
                            <span className="material-symbols-outlined text-white text-6xl">{status === 'listening' ? 'mic' : 'mic_off'}</span>
                        </button>
                    </div>

                    {/* Transcript Area */}
                    <div className="w-full max-w-2xl bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 lg:p-8 shadow-sm max-h-[400px] overflow-y-auto">
                        <div className="flex flex-col gap-6">
                            {messages.slice(-2).map((msg, idx) => (
                                <div key={idx} className="flex gap-4">
                                    <div className={`shrink-0 size-10 rounded-full flex items-center justify-center mt-1 ${msg.sender === 'assistant' ? 'bg-primary/10 text-primary' : 'bg-slate-100 text-slate-600'}`}>
                                        <span className="material-symbols-outlined">{msg.sender === 'assistant' ? 'smart_toy' : 'person'}</span>
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">{msg.sender === 'assistant' ? 'Assistant' : 'You'}</span>
                                        <p className="text-xl md:text-2xl text-slate-800 dark:text-slate-200 font-medium leading-relaxed">
                                            {msg.text}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {messages.length === 0 && <p className="text-center text-slate-400">Conversation will appear here...</p>}
                        </div>
                    </div>

                    {/* Main Controls */}
                    <div className="flex flex-wrap justify-center gap-4 w-full pt-4">
                        <button
                            onClick={() => navigate('/review')}
                            className="flex items-center gap-3 h-16 px-8 rounded-2xl bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-lg font-bold hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-all active:scale-95 border-2 border-transparent">
                            <span className="material-symbols-outlined text-3xl">check</span>
                            Finish & Review
                        </button>
                    </div>
                </div>

                {/* RIGHT COLUMN: Summary / Context Sidebar (Static for now) */}
                <div className="hidden lg:flex flex-col flex-1 lg:max-w-md w-full opacity-50 pointer-events-none">
                    {/* ... (Summary simplified/hidden for prototype focus on voice) ... */}
                    <p className="text-center mt-10">Real-time summary updates coming soon.</p>
                </div>
            </main>
        </div>
    );
};

export default VoiceAssistantPage;
