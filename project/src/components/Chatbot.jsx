import React, { useState } from "react";

function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]); // {sender: 'user'|'bot', text: string}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text }),
      });

      const data = await res.json();

      const botMessage = {
        sender: "bot",
        text: data.answer || "Sorry, I could not get an answer.",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error contacting server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg"
      >
        {isOpen ? "Close Chat" : "Chat with RAG Bot"}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="mt-2 w-80 h-96 bg-white rounded-lg shadow-xl flex flex-col border border-gray-200">
          <div className="px-3 py-2 border-b border-gray-200 font-semibold text-gray-800">
            RAG Chatbot
          </div>

          {/* Messages */}
          <div className="flex-1 p-3 overflow-y-auto text-sm space-y-2">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-3 py-2 rounded-lg ${
                    msg.sender === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-800"
                  } max-w-[80%] whitespace-pre-wrap`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="text-xs text-gray-500">Thinking...</div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-2 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Ask something about the PDF..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button
                type="submit"
                className="bg-blue-600 text-white text-sm px-3 py-1 rounded disabled:opacity-50"
                disabled={loading}
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default Chatbot;
