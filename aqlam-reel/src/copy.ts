/**
 * All on-screen copy. Edit text here without touching animations.
 * Words are animated one at a time (split on spaces), so keep each
 * line short — 1 line reads best on a phone.
 */
export const COPY = {
  brandName: "أقلام",

  hook: {
    line1: "الساعة ٩ بالليل…",
    line2: "والواجب للحين ما خلص 😩",
  },

  pain: {
    lines: ["الولد تعبان", "وإنت تعبان", "والرياضيات ما لها خلق"],
  },

  turn: {
    line: "خلّ الشرح علينا",
  },

  solution: {
    tutorTitle: "مدرس رياضيات – الصف السادس",
    tutorName: "أ. أحمد",
    liveBadge: "حصة مباشرة",
    screenHeader: "حصتك الحين",
    joinButton: "ادخل الحصة",
    benefits: [
      "حصص مباشرة ١ على ١",
      "كل المواد وكل الصفوف",
      "الباقة ما تنتهي وتتقسم بين عيالك",
    ],
  },

  offer: {
    main: "١٢ حصة بـ ٧٠٠ درهم",
    sub: "يعني أقل من ٦٠ درهم للحصة",
  },

  cta: {
    main: "حمّل التطبيق الحين",
    store: "متوفر على App Store",
    whatsapp: "أو كلمنا واتساب",
  },
} as const;
