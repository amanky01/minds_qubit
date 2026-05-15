import Head from "next/head";
import Link from "next/link";
import { useState } from "react";
import styles from "@/styles/Blog.module.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function Blog() {
  const [field, setField] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!field.trim()) {
      setError("Please enter a field/topic");
      return;
    }

    setIsGenerating(true);
    setError("");
    setGeneratedContent("");

    try {
      const response = await fetch('/api/generate-blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate blog');
      }

      setGeneratedContent(data.content);
    } catch {
      setError("Failed to generate blog content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyContent = () => {
    navigator.clipboard.writeText(generatedContent);
    // You could add a toast notification here
  };

  return (
    <>
      <Head>
        <title>Technical Blog Generator - TheMindSqubit</title>
        <meta name="description" content="Generate technical blog content with AI assistance" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className={styles.container}>
        <Header />
        
        <main className={styles.main}>
          <div className={styles.content}>
            <div className={styles.header}>
              <div className={styles.headerTop}>
                <Link href="/" className={styles.backButton}>
                  ← Back to Home
                </Link>
              </div>
              <h1>Technical Blog Generator</h1>
              <p>Generate professional technical blog content with AI assistance</p>
            </div>

            <div className={styles.formSection}>
              <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.inputGroup}>
                  <label htmlFor="field">What field/topic would you like to write about?</label>
                  <input
                    type="text"
                    id="field"
                    value={field}
                    onChange={(e) => setField(e.target.value)}
                    placeholder="e.g., Machine Learning, Web Development, Cybersecurity, Blockchain..."
                    className={styles.input}
                    disabled={isGenerating}
                  />
                  {error && <p className={styles.error}>{error}</p>}
                </div>
                
                <button 
                  type="submit" 
                  className={styles.generateButton}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <div className={styles.spinner}></div>
                      Generating...
                    </>
                  ) : (
                    'Generate Blog'
                  )}
                </button>
              </form>
            </div>

            {generatedContent && (
              <div className={styles.resultSection}>
                <div className={styles.resultHeader}>
                  <h2>Generated Blog Content</h2>
                  <button 
                    onClick={handleCopyContent}
                    className={styles.copyButton}
                  >
                    Copy Content
                  </button>
                </div>
                
                <div className={styles.blogContent}>
                  <pre className={styles.contentText}>{generatedContent}</pre>
                </div>
              </div>
            )}

            <div className={styles.features}>
              <h2>Why Use Our Blog Generator?</h2>
              <div className={styles.featureGrid}>
                <div className={styles.feature}>
                  <div className={styles.featureIcon}>🚀</div>
                  <h3>Fast Generation</h3>
                  <p>Get professional blog content in seconds</p>
                </div>
                <div className={styles.feature}>
                  <div className={styles.featureIcon}>🎯</div>
                  <h3>Technical Accuracy</h3>
                  <p>AI-powered content with technical precision</p>
                </div>
                <div className={styles.feature}>
                  <div className={styles.featureIcon}>📝</div>
                  <h3>SEO Optimized</h3>
                  <p>Content structured for search engines</p>
                </div>
                <div className={styles.feature}>
                  <div className={styles.featureIcon}>🔄</div>
                  <h3>Easy Customization</h3>
                  <p>Modify and adapt content as needed</p>
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
} 