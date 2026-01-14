import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const ReviewPage = () => {
    const navigate = useNavigate();
    const [generated, setGenerated] = useState(false);

    const handleGenerate = () => {
        setGenerated(true);
        setTimeout(() => setGenerated(false), 3000);
    };

    return (
        <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display transition-colors duration-200">
            {/* Top Navigation */}
            <header className="bg-surface-light dark:bg-surface-dark border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
                <div className="max-w-[1400px] mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4 text-slate-900 dark:text-white">
                        <div className="size-10 bg-primary rounded-lg flex items-center justify-center text-white">
                            <span className="material-symbols-outlined text-2xl">security</span>
                        </div>
                        <h2 className="text-xl md:text-2xl font-bold leading-tight tracking-tight">Bureaucracy Companion</h2>
                    </div>
                    <div className="flex items-center gap-6">
                        <nav className="hidden md:flex items-center gap-8">
                            <Link className="text-slate-600 dark:text-slate-300 text-lg font-medium hover:text-primary transition-colors" to="/">Home</Link>
                            <a className="text-primary text-lg font-medium underline underline-offset-4" href="#">My Forms</a>
                            <a className="text-slate-600 dark:text-slate-300 text-lg font-medium hover:text-primary transition-colors" href="#">Help</a>
                        </nav>
                        <div aria-label="User profile" className="size-12 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden border-2 border-slate-300 dark:border-slate-600">
                            <div className="bg-center bg-no-repeat w-full h-full bg-cover" data-alt="Portrait of an elderly woman smiling" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuANyQYBJDQBmMbNDpESjKCNmlordV1x2uItrsLZktMc0iUEVain8vK1AbWwp70B6kBlk64M180I2AXgPHrDaQQcgPao5JHPxKgqCqFytwiL_UOlJieUJbhlqhvjRhKRF7OWJa9dX3PlYzP4sN00-txYDi__6R6aQfIkHlIEHXA9n2kCe2RrrqA5w5Qs3ItbiTlkSpGqDzgGdq23cDbfFHFNxHYVd8q6rTh99IVnIaac3KntgGf1ckZwBvE24C1WjnSsN-QSEManOKHa")' }}></div>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-grow flex flex-col items-center py-8 px-4 md:px-8 max-w-[1400px] mx-auto w-full">
                {/* Page Heading */}
                <div className="w-full mb-8">
                    <h1 className="text-3xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-white mb-2">Step 4 of 5: Review your details</h1>
                    <p className="text-slate-600 dark:text-slate-400 text-xl font-normal max-w-2xl">Please check your simplified answers on the left against the official form preview on the right.</p>
                </div>

                {/* Safety Banner */}
                <div className="w-full bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800 rounded-xl p-6 mb-8 flex flex-col md:flex-row items-center gap-6 shadow-sm">
                    <div className="flex-shrink-0 size-16 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center text-green-600 dark:text-green-300">
                        <span className="material-symbols-outlined text-4xl">verified_user</span>
                    </div>
                    <div className="flex-grow text-center md:text-left">
                        <h3 className="text-2xl font-bold text-green-800 dark:text-green-300 mb-1">Safety Check Passed</h3>
                        <p className="text-green-700 dark:text-green-400 text-lg">No existing benefits (Pension, Housing allowance) will be affected by this registration. Your data is secure.</p>
                    </div>
                    <div className="flex-shrink-0">
                        <button className="flex items-center gap-2 text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-800 px-4 py-2 rounded-lg font-medium text-lg transition-colors">
                            <span className="material-symbols-outlined">info</span>
                            Details
                        </button>
                    </div>
                </div>

                {/* Main Split Content */}
                <div className="flex flex-col lg:flex-row gap-8 w-full h-full min-h-[600px]">
                    {/* LEFT COLUMN: Simplified Answers */}
                    <div className="w-full lg:w-5/12 flex flex-col gap-6">
                        <div className="flex items-center justify-between mb-2">
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">assignment_ind</span>
                                Your Answers
                            </h2>
                            <button className="text-primary font-medium text-lg hover:underline flex items-center gap-1">
                                <span className="material-symbols-outlined text-lg">translate</span>
                                Switch Language
                            </button>
                        </div>
                        {/* Cards Container */}
                        <div className="flex flex-col gap-4 overflow-y-auto pr-2 custom-scrollbar">
                            {/* Card 1: Personal Info */}
                            <div className="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm hover:border-primary transition-colors group cursor-pointer relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-2 h-full bg-primary/20 group-hover:bg-primary transition-colors"></div>
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Personal Information</h3>
                                    <button aria-label="Edit Personal Information" className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full text-primary">
                                        <span className="material-symbols-outlined">edit</span>
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Full Name</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Maria Schmidt</p>
                                    </div>
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Nationality</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Italian</p>
                                    </div>
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Date of Birth</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">15.03.1952</p>
                                    </div>
                                </div>
                            </div>
                            {/* Card 2: Move Details */}
                            <div className="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm hover:border-primary transition-colors group cursor-pointer relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-2 h-full bg-slate-200 dark:bg-slate-700 group-hover:bg-primary transition-colors"></div>
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Move Details</h3>
                                    <button aria-label="Edit Move Details" className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full text-primary">
                                        <span className="material-symbols-outlined">edit</span>
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Move-in Date</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">1st November 2023</p>
                                    </div>
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">New Address</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Hauptstraße 5, 80331 München</p>
                                    </div>
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Previous Address</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Musterstraße 12, 10115 Berlin</p>
                                    </div>
                                </div>
                            </div>
                            {/* Card 3: Additional */}
                            <div className="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm hover:border-primary transition-colors group cursor-pointer relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-2 h-full bg-slate-200 dark:bg-slate-700 group-hover:bg-primary transition-colors"></div>
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Family Status</h3>
                                    <button aria-label="Edit Family Status" className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full text-primary">
                                        <span className="material-symbols-outlined">edit</span>
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Marital Status</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Widowed</p>
                                    </div>
                                    <div>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Religion</p>
                                        <p className="text-slate-900 dark:text-white text-xl font-medium">Roman Catholic</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Official Form Preview */}
                    <div className="w-full lg:w-7/12 flex flex-col gap-4">
                        <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2 mb-2">
                            <span className="material-symbols-outlined text-slate-500">description</span>
                            Official Form Preview (Anmeldung)
                        </h2>
                        <div className="relative w-full bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-300 dark:border-slate-700 overflow-hidden flex-grow min-h-[600px] shadow-inner">
                            {/* Document Background */}
                            <div aria-hidden="true" className="absolute inset-4 bg-white shadow-lg rounded-sm overflow-hidden p-8 opacity-90 select-none pointer-events-none">
                                {/* Abstract Representation of a German Form */}
                                <div className="border-b-2 border-black pb-4 mb-6 flex justify-between items-end">
                                    <div>
                                        <div className="h-4 w-32 bg-slate-800 mb-2"></div>
                                        <div className="h-8 w-64 bg-slate-900 font-serif text-2xl font-bold">ANMELDUNG</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="h-20 w-20 border border-slate-400 bg-slate-50"></div>
                                    </div>
                                </div>
                                <div className="grid grid-cols-12 gap-x-4 gap-y-6 text-[10px] text-slate-800 font-mono leading-none">
                                    <div className="col-span-12 border-b border-slate-300 pb-1 font-bold">Persönliche Angaben</div>
                                    <div className="col-span-6">
                                        <div className="mb-1">Name</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">SCHMIDT</div>
                                    </div>
                                    <div className="col-span-6">
                                        <div className="mb-1">Vorname</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">MARIA</div>
                                    </div>
                                    <div className="col-span-4">
                                        <div className="mb-1">Geburtsdatum</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">15.03.1952</div>
                                    </div>
                                    <div className="col-span-4">
                                        <div className="mb-1">Geschlecht</div>
                                        <div className="border border-slate-400 h-8 flex items-center px-2">Weiblich</div>
                                    </div>
                                    <div className="col-span-4">
                                        <div className="mb-1">Staatsangehörigkeit</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">ITALIENISCH</div>
                                    </div>
                                    <div className="col-span-12 border-b border-slate-300 pb-1 font-bold mt-4">Neue Wohnung</div>
                                    <div className="col-span-3">
                                        <div className="mb-1">PLZ</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">80331</div>
                                    </div>
                                    <div className="col-span-5">
                                        <div className="mb-1">Ort</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">MÜNCHEN</div>
                                    </div>
                                    <div className="col-span-4">
                                        <div className="mb-1">Einzugsdatum</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">01.11.2023</div>
                                    </div>
                                    <div className="col-span-9">
                                        <div className="mb-1">Straße</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">HAUPTSTRAßE</div>
                                    </div>
                                    <div className="col-span-3">
                                        <div className="mb-1">Hausnr.</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">5</div>
                                    </div>
                                    <div className="col-span-12 border-b border-slate-300 pb-1 font-bold mt-4">Bisherige Wohnung</div>
                                    <div className="col-span-12">
                                        <div className="mb-1">Anschrift</div>
                                        <div className="border border-slate-400 h-8 bg-blue-50/50 flex items-center px-2">MUSTERSTRAßE 12, 10115 BERLIN</div>
                                    </div>
                                    <div className="col-span-12 border-b border-slate-300 pb-1 font-bold mt-4">Rechtliche Hinweise</div>
                                    <div className="col-span-12 text-[8px] leading-tight text-slate-500">
                                        Hiermit bestätige ich die Richtigkeit der Angaben. Falsche Angaben können als Ordnungswidrigkeit geahndet werden. § 19 BMG.
                                    </div>
                                </div>
                            </div>
                            {/* Overlay Highlights (Simulated Interactive Elements) */}
                            <div className="absolute inset-4 pointer-events-none">
                                {/* Highlight Box for Name (matches simplified view card 1) */}
                                <div className="absolute top-[138px] left-[32px] w-[220px] h-[36px] border-2 border-primary bg-primary/10 rounded">
                                    <div className="absolute -top-3 -right-3 bg-primary text-white rounded-full size-6 flex items-center justify-center text-xs font-bold shadow-sm">1</div>
                                </div>
                                {/* Highlight Box for Address (matches simplified view card 2) */}
                                <div className="absolute top-[310px] left-[32px] w-[500px] h-[36px] border-2 border-primary/50 bg-primary/5 rounded border-dashed">
                                    <div className="absolute -top-3 -right-3 bg-slate-500 text-white rounded-full size-6 flex items-center justify-center text-xs font-bold shadow-sm">2</div>
                                </div>
                            </div>
                            {/* Zoom Controls */}
                            <div className="absolute bottom-4 right-4 flex gap-2">
                                <button className="bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 p-2 rounded-lg shadow-md hover:bg-slate-50 dark:hover:bg-slate-600 border border-slate-200 dark:border-slate-600">
                                    <span className="material-symbols-outlined">add</span>
                                </button>
                                <button className="bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 p-2 rounded-lg shadow-md hover:bg-slate-50 dark:hover:bg-slate-600 border border-slate-200 dark:border-slate-600">
                                    <span className="material-symbols-outlined">remove</span>
                                </button>
                            </div>
                        </div>
                        <p className="text-sm text-slate-500 dark:text-slate-400 italic text-center">
                            This is a preview of the document that will be generated for the citizens' office (Bürgeramt).
                        </p>
                    </div>
                </div>
                {/* Action Footer */}
                <div className="w-full mt-12 bg-white dark:bg-slate-800 rounded-t-2xl border-t border-slate-200 dark:border-slate-700 p-6 md:p-8 sticky bottom-0 z-20 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
                    <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                        <button
                            onClick={() => navigate('/assistant')}
                            className="w-full md:w-auto px-8 h-16 rounded-xl border-2 border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 font-bold text-xl flex items-center justify-center gap-3 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                            <span className="material-symbols-outlined text-3xl">arrow_back</span>
                            Back to questions
                        </button>
                        <div className="flex flex-col items-center md:items-end">
                            <button
                                onClick={handleGenerate}
                                className="w-full md:w-auto px-12 h-20 bg-primary hover:bg-blue-700 text-white rounded-xl shadow-lg shadow-blue-500/30 font-bold text-2xl flex items-center justify-center gap-4 transition-all transform hover:scale-[1.02]">
                                {generated ? "Success!" : "Generate Final Form"}
                                <span className="material-symbols-outlined text-4xl">{generated ? "check_circle" : "description"}</span>
                            </button>
                            <p className="mt-2 text-slate-500 dark:text-slate-400 text-sm font-medium">
                                <span className="material-symbols-outlined align-middle text-sm mr-1">lock</span>
                                Your information is encrypted and stored locally.
                            </p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ReviewPage;
