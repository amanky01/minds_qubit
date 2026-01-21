# TheMindSqubit - AI Agents Platform

A modern, modular website showcasing different AI agents designed to help users accomplish various tasks. Built with Next.js, TypeScript, and modern CSS.

## 🚀 Features

- **Modern Design**: Beautiful gradient backgrounds with glassmorphism effects
- **Responsive Layout**: Fully responsive design that works on all devices
- **Modular Architecture**: Clean, reusable components for easy maintenance
- **Interactive UI**: Smooth animations and hover effects
- **Category Filtering**: Filter AI agents by category
- **6 AI Agents**: Specialized agents for different tasks

## 🧠 AI Agents

1. **CodeCraft** 💻 - Programming assistant for code generation and debugging
2. **DataViz** 📊 - Data visualization and analytics
3. **ContentCreator** ✍️ - Content generation and creative writing
4. **DesignMaster** 🎨 - Design and visual content creation
5. **ResearchPro** 🔍 - Research and data analysis
6. **LanguageTutor** 🌍 - Language learning and practice

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Header.tsx      # Navigation header
│   │   ├── Hero.tsx        # Hero section with floating icons
│   │   ├── CategoryFilter.tsx # Category filtering component
│   │   ├── AgentCard.tsx   # Individual agent card
│   │   ├── AgentsGrid.tsx  # Grid layout for agents
│   │   ├── About.tsx       # About section
│   │   └── Footer.tsx      # Footer component
│   ├── data/
│   │   └── aiAgents.ts     # AI agents data and types
│   ├── pages/
│   │   └── index.tsx       # Main page component
│   └── styles/
│       └── Home.module.css # Styled components
├── public/                 # Static assets
└── package.json           # Dependencies and scripts
```

## 🛠️ Technologies Used

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **CSS Modules** - Scoped styling
- **Modern CSS** - Grid, Flexbox, Animations
- **Responsive Design** - Mobile-first approach

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to `http://localhost:3000`

## 📱 Responsive Design

The website is fully responsive with breakpoints for:
- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: 480px - 767px
- **Small Mobile**: Below 480px

## 🎨 Design Features

- **Gradient Backgrounds**: Beautiful purple-blue gradients
- **Glassmorphism**: Translucent cards with backdrop blur
- **Floating Animations**: Animated icons in hero section
- **Hover Effects**: Interactive buttons and cards
- **Smooth Transitions**: CSS transitions for better UX

## 🔧 Customization

### Adding New AI Agents

1. Edit `src/data/aiAgents.ts`
2. Add new agent object with required properties:
   ```typescript
   {
     id: number,
     name: string,
     description: string,
     icon: string,
     category: string,
     features: string[]
   }
   ```

### Styling

- Main styles: `src/styles/Home.module.css`
- Component-specific styles are co-located with components
- Uses CSS custom properties for consistent theming

### Components

Each component is self-contained and reusable:
- **Header**: Navigation with logo and menu
- **Hero**: Landing section with call-to-action
- **CategoryFilter**: Interactive category selection
- **AgentCard**: Individual agent display
- **AgentsGrid**: Responsive grid layout
- **About**: Company information and stats
- **Footer**: Contact information and links

## 🚀 Deployment

The project is ready for deployment on:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- Any static hosting service

## 🔮 Future Enhancements

- [ ] Backend integration for dynamic agent data
- [ ] User authentication and profiles
- [ ] Agent interaction interface
- [ ] Real-time chat with AI agents
- [ ] Analytics dashboard
- [ ] Dark/Light theme toggle
- [ ] Internationalization (i18n)

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

Built with ❤️ for TheMindSqubit
