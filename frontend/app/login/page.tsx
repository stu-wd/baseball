"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const result = await signIn("credentials", {
      username: form.get("username"),
      password: form.get("password"),
      redirect: false,
    });
    if (result?.ok) {
      router.push("/standings");
    } else {
      setError("Invalid username or password");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="bg-gray-800 p-8 rounded-lg w-80 flex flex-col gap-4"
      >
        <h1 className="text-xl font-bold text-center">⚾ Baseball Dashboard</h1>
        {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        <input
          name="username"
          placeholder="Username"
          required
          className="bg-gray-700 px-3 py-2 rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          required
          className="bg-gray-700 px-3 py-2 rounded text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 py-2 rounded text-sm font-medium"
        >
          Sign in
        </button>
      </form>
    </div>
  );
}
