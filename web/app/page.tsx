import { ApiConfigBanner } from "@/components/ApiConfigBanner";
import { ChatApp } from "@/components/ChatApp";
import { DisclaimerBar } from "@/components/DisclaimerBar";
import { HeaderBar } from "@/components/HeaderBar";

export default function Home() {
  return (
    <div className="flex min-h-dvh flex-col">
      <ApiConfigBanner />
      <HeaderBar />
      <main className="flex flex-1 flex-col px-4 pb-6 pt-5 sm:px-6">
        <ChatApp />
      </main>
      <DisclaimerBar />
    </div>
  );
}
