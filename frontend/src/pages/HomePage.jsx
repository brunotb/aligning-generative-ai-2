import { useNavigate } from 'react-router-dom';

const HomePage = () => {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col min-h-screen">
            {/* Top Navigation */}
            <header className="w-full bg-white dark:bg-background-dark border-b border-[#f0f2f4] dark:border-[#2a3441] px-6 py-4 lg:px-10 flex items-center justify-between sticky top-0 z-50">
                <div className="flex items-center gap-4">
                    <div className="size-10 flex items-center justify-center text-primary bg-primary/10 rounded-lg">
                        <span className="material-symbols-outlined text-3xl">assistant</span>
                    </div>
                    <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-[#111318] dark:text-white">Amt-Assistent</h1>
                </div>
                <div>
                    <button className="flex items-center gap-2 cursor-pointer bg-background-light dark:bg-[#1a2230] hover:bg-[#ebebeb] dark:hover:bg-[#252f40] transition-colors rounded-xl h-10 px-4 text-[#111318] dark:text-white font-medium">
                        <span className="material-symbols-outlined text-[20px]">text_fields</span>
                        <span className="text-sm font-bold">A/A+</span>
                    </button>
                </div>
            </header>

            {/* Main Split Layout */}
            <main className="flex flex-col lg:flex-row grow">
                {/* Sidebar: Context & Explanation */}
                <aside className="w-full lg:w-[35%] bg-background-light dark:bg-[#1a2230] p-8 lg:p-12 xl:p-16 flex flex-col justify-center gap-8 order-2 lg:order-1 border-t lg:border-t-0 lg:border-r border-[#dbdfe6] dark:border-[#2a3441]">
                    <div className="flex flex-col gap-6">
                        {/* English Explanation */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-primary">
                                <span className="material-symbols-outlined">translate</span>
                                <span className="text-xs font-bold uppercase tracking-wider">English</span>
                            </div>
                            <p className="text-xl lg:text-2xl font-medium leading-relaxed">
                                I help you with your registration. We just talk, and I fill the forms for you.
                            </p>
                        </div>
                        <div className="h-px w-full bg-[#dbdfe6] dark:bg-[#2a3441]"></div>
                        {/* German Explanation */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-primary">
                                <span className="material-symbols-outlined">translate</span>
                                <span className="text-xs font-bold uppercase tracking-wider">Deutsch</span>
                            </div>
                            <p className="text-xl lg:text-2xl font-medium leading-relaxed text-[#111318] dark:text-white">
                                Ich helfe Ihnen bei Ihrer Anmeldung. Wir sprechen einfach, und ich fülle die Formulare für Sie aus.
                            </p>
                        </div>
                    </div>
                    {/* Trust Indicators */}
                    <div className="mt-8 flex gap-4">
                        <div className="flex items-center gap-2 px-3 py-1 bg-white dark:bg-background-dark rounded-full shadow-sm border border-[#dbdfe6] dark:border-[#2a3441]">
                            <span className="material-symbols-outlined text-green-600 text-[18px]">security</span>
                            <span className="text-xs font-bold">Secure Data</span>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-1 bg-white dark:bg-background-dark rounded-full shadow-sm border border-[#dbdfe6] dark:border-[#2a3441]">
                            <span className="material-symbols-outlined text-blue-600 text-[18px]">verified</span>
                            <span className="text-xs font-bold">Official Forms</span>
                        </div>
                    </div>
                </aside>

                {/* Main Content: Action Area */}
                <section className="w-full lg:w-[65%] bg-white dark:bg-background-dark p-6 lg:p-12 xl:p-20 flex flex-col items-center justify-center text-center order-1 lg:order-2">
                    {/* Hero Image/Graphic */}
                    <div className="mb-10 w-full max-w-lg rounded-2xl overflow-hidden shadow-sm border border-[#f0f2f4] dark:border-[#2a3441]">
                        <div className="w-full h-48 sm:h-64 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/20 dark:to-indigo-900/20 flex items-center justify-center" data-alt="Soft abstract blue gradient background with friendly shapes">
                            <span className="material-symbols-outlined text-primary/30 text-9xl">forum</span>
                        </div>
                    </div>
                    <h1 className="text-4xl lg:text-5xl xl:text-6xl font-black tracking-tight text-[#111318] dark:text-white mb-4">
                        Welcome to Amt-Assistent
                    </h1>
                    <h2 className="text-lg lg:text-xl text-[#616f89] dark:text-gray-400 font-normal mb-10 max-w-xl">
                        Bureaucracy made simple. <br className="hidden sm:block" /> No typing, just talking.
                    </h2>
                    {/* Features Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl mb-12">
                        {/* Feature 1 */}
                        <div className="flex flex-col items-center gap-3 p-4 rounded-xl border border-transparent hover:border-[#dbdfe6] hover:bg-background-light dark:hover:bg-[#1a2230] transition-all">
                            <div className="size-16 rounded-full bg-blue-50 dark:bg-blue-900/30 text-primary flex items-center justify-center mb-1">
                                <span className="material-symbols-outlined text-4xl">mic</span>
                            </div>
                            <h3 className="text-lg font-bold">Speak</h3>
                            <p className="text-sm text-[#616f89] dark:text-gray-400">Sprechen</p>
                        </div>
                        {/* Feature 2 */}
                        <div className="flex flex-col items-center gap-3 p-4 rounded-xl border border-transparent hover:border-[#dbdfe6] hover:bg-background-light dark:hover:bg-[#1a2230] transition-all">
                            <div className="size-16 rounded-full bg-blue-50 dark:bg-blue-900/30 text-primary flex items-center justify-center mb-1">
                                <span className="material-symbols-outlined text-4xl">hearing</span>
                            </div>
                            <h3 className="text-lg font-bold">Understand</h3>
                            <p className="text-sm text-[#616f89] dark:text-gray-400">Verstehen</p>
                        </div>
                        {/* Feature 3 */}
                        <div className="flex flex-col items-center gap-3 p-4 rounded-xl border border-transparent hover:border-[#dbdfe6] hover:bg-background-light dark:hover:bg-[#1a2230] transition-all">
                            <div className="size-16 rounded-full bg-blue-50 dark:bg-blue-900/30 text-primary flex items-center justify-center mb-1">
                                <span className="material-symbols-outlined text-4xl">support_agent</span>
                            </div>
                            <h3 className="text-lg font-bold">Help</h3>
                            <p className="text-sm text-[#616f89] dark:text-gray-400">Hilfe</p>
                        </div>
                    </div>
                    {/* Primary CTA Button */}
                    <button
                        onClick={() => navigate('/assistant')}
                        className="group relative flex w-full max-w-md cursor-pointer items-center justify-center gap-4 overflow-hidden rounded-2xl bg-primary px-8 py-6 shadow-lg shadow-blue-200 dark:shadow-blue-900/20 transition-transform hover:scale-[1.02] active:scale-[0.98]">
                        <div className="relative flex items-center justify-center">
                            <span className="material-symbols-outlined text-white text-3xl animate-pulse">mic</span>
                        </div>
                        <div className="flex flex-col items-start text-white">
                            <span className="text-lg lg:text-xl font-black leading-tight">Start Conversation</span>
                            <span className="text-sm lg:text-base font-medium opacity-90">Gespräch starten</span>
                        </div>
                        <span className="absolute right-6 opacity-0 transition-opacity group-hover:opacity-100 material-symbols-outlined text-white/50">arrow_forward</span>
                    </button>
                </section>
            </main>
        </div>
    );
};

export default HomePage;
