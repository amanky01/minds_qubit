export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
}

export const aiAgents: Agent[] = [
  {
    id: 1,
    name: "CodeCraft",
    description: "Your AI programming assistant that helps you write, debug, and optimize code across multiple languages.",
    icon: "💻",
    category: "Development",
    features: ["Code Generation", "Bug Detection", "Code Review", "Documentation"]
  },
  {
    id: 2,
    name: "DataViz",
    description: "Transform your data into stunning visualizations and insights with AI-powered analytics.",
    icon: "📊",
    category: "Analytics",
    features: ["Data Analysis", "Chart Generation", "Insight Discovery", "Report Creation"]
  },
  {
    id: 3,
    name: "ContentCreator",
    description: "Generate engaging content, articles, and creative writing with AI assistance.",
    icon: "✍️",
    category: "Content",
    features: ["Article Writing", "Blog Posts", "Social Media", "Creative Stories"]
  },
  {
    id: 4,
    name: "DesignMaster",
    description: "Create beautiful designs, logos, and visual content with AI-powered design tools.",
    icon: "🎨",
    category: "Design",
    features: ["Logo Design", "UI/UX", "Graphics", "Branding"]
  },
  {
    id: 5,
    name: "ResearchPro",
    description: "Conduct comprehensive research and gather insights from multiple sources efficiently.",
    icon: "🔍",
    category: "Research",
    features: ["Source Analysis", "Fact Checking", "Trend Analysis", "Report Generation"]
  },
  {
    id: 6,
    name: "LanguageTutor",
    description: "Learn new languages with personalized AI tutoring and conversation practice.",
    icon: "🌍",
    category: "Education",
    features: ["Conversation Practice", "Grammar Correction", "Vocabulary Building", "Cultural Context"]
  }
];

export const categories = ["All", "Development", "Analytics", "Content", "Design", "Research", "Education"]; 