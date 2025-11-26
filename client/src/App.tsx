import { useState } from "react";
import Chat from "./components/chat";
import { nanoid } from "nanoid";

const App = () => {
  const [chatId, setChatId] = useState<string>(nanoid());

  return <Chat chatId={chatId} setChatId={(newChatId: string) => setChatId(newChatId)} />
}

export default App;