import { useEffect, useRef } from 'react';
import { useFormStore } from '../store/formStore';

export function ChatHistory() {
    const transcripts = useFormStore((state) => state.transcripts);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [transcripts]);

    return (
        <div className="h-full flex flex-col bg-white rounded-lg shadow-lg">
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
                <h2 className="text-lg font-semibold text-gray-800">Conversation</h2>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 space-y-4"
            >
                {transcripts.length === 0 ? (
                    <p className="text-gray-400 text-center italic">
                        Start speaking to begin the conversation...
                    </p>
                ) : (
                    transcripts.map((transcript, index) => (
                        <div
                            key={index}
                            className={`flex ${transcript.speaker === 'user' ? 'justify-end' : 'justify-start'
                                }`}
                        >
                            <div
                                className={`max-w-[80%] rounded-lg px-4 py-2 ${transcript.speaker === 'user'
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-100 text-gray-800'
                                    }`}
                            >
                                <p className="text-xs font-semibold mb-1 opacity-70">
                                    {transcript.speaker === 'user' ? 'User' : 'Assistant'}
                                </p>
                                <p className="text-sm">{transcript.text}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
