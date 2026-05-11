"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function ScrollCTA() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const past = y > window.innerHeight * 0.9;
      const nearEnd = y > max - 600;
      setShow(past && !nearEnd);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <AnimatePresence>
      {show && (
        <motion.a
          href="#predict"
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ type: "spring", stiffness: 320, damping: 28 }}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          className="fixed bottom-6 right-6 z-40 btn-primary px-5 py-3 inline-flex items-center gap-2 text-sm shadow-lg"
          style={{ boxShadow: "0 14px 32px -10px rgba(194,65,12,0.55)" }}
        >
          <Sparkles size={15} /> ลองโมเดลเอง
        </motion.a>
      )}
    </AnimatePresence>
  );
}
