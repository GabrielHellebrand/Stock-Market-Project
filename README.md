Software Requirements Specification (SRS)

Finance Tracker & Prediction System

Version: 1.0

Date: July 8, 2025

Prepared by: Gabriel Hellebrand & Matthew Hanna

________________________________________

1\. Introduction

1.1 Purpose

This document outlines the software requirements for the development of the Finance Tracker & Prediction System, a web-based and mobile-accessible application for tracking financial data from S&P 500 and NASDAQ 100 companies. The application will also provide stock market predictions using machine learning tools like XGBoost, tailored for both beginner investors and advanced users (e.g., CEOs).

1.2 Intended Audience

-  Investors with no prior stock market experience

-  C-level Executives and Analysts requiring advanced financial insights

-  Developers and Testers building the system

-  Data Scientists and ML Engineers implementing prediction models

1.3 Scope

The Finance Tracker & Prediction System will:

-  Track real-time and historical financial data from S&P 500 and NASDAQ 100 companies

-  Display earnings reports, charts, and company fundamentals

-  Use XGBoost and other ML tools to predict stock movement

-  Offer both simplified UI for beginners and detailed dashboards for advanced users

-  Provide notification and alert systems based on trends or user-defined rules

1.4 Definitions

-  XGBoost: A scalable, high-performance gradient boosting library for machine learning.

-  S&P 500: An index tracking 500 large-cap U.S. companies.

-  NASDAQ 100: An index of 100 of the largest non-financial companies on NASDAQ.

________________________________________

2\. Overall Description

2.1 Product Perspective

This is a standalone web/mobile application with a RESTful backend, integrated with third-party financial APIs (e.g., Alpha Vantage, Yahoo Finance, or IEX Cloud), and ML model endpoints served via FastAPI.

2.2 Product Functions

-  Display key stock data (price, volume, P/E ratio, etc.)

-  Show historical stock trends via interactive graphs

-  Enable stock prediction using trained XGBoost models

-  Generate watchlists and alerts for user-specified stocks

-  Provide dual-mode interface (Novice / Advanced)

2.3 User Classes and Characteristics

User Type  Description  Skill Level

Novice User  Interested in market trends and learning about stocks  No prior experience

Experienced Trader  Wants advanced analytics and decision-making tools  Moderate

CEO/Executive  Needs macro and micro insights with strategic decision-making focus  High

2.4 Operating Environment

-  Frontend: React.js (Web), React Native or Flutter (Mobile)

-  Backend: FastAPI (Python), PostgreSQL

-  ML Engine: Python-based XGBoost models served via API

-  Hosting: AWS/GCP/Azure

-  Browser Support: Chrome, Firefox, Safari, Edge

2.5 Design and Implementation Constraints

-  Use only publicly available or licensed financial APIs

-  Predictions are for informational purposes only, not financial advice

-  All ML predictions must include a confidence interval

2.6 User Documentation

-  Online help and onboarding tutorials

-  FAQs and tooltips throughout the UI

-  Glossary of financial terms

________________________________________

3\. Specific Requirements

3.1 Functional Requirements

3.1.1 Stock Data Tracking

-  FR1.1: The system shall fetch and update stock data from S&P 500 and NASDAQ 100 every 5 minutes.

-  FR1.2: The system shall allow users to search for companies by name or ticker.

-  FR1.3: The system shall show real-time, intraday, and historical charts.

3.1.2 Prediction Engine

-  FR2.1: The system shall expose an API endpoint that returns stock movement prediction based on the XGBoost model.

-  FR2.2: The system shall return prediction confidence intervals.

-  FR2.3: The system shall retrain the model weekly using updated data.

3.1.3 User Interface

-  FR3.1: The UI shall provide a beginner mode with simplified graphs and explanations.

-  FR3.2: The UI shall provide an advanced mode with full metrics, filters, and financial indicators.

-  FR3.3: Users shall be able to toggle between UI modes.

-  FR3.4: The system shall offer dark and light themes.

3.1.4 Watchlists & Alerts

-  FR4.1: Users shall be able to create personalized watchlists.

-  FR4.2: Users shall receive email/push alerts when certain thresholds (e.g., price drop/rise) are hit.

-  FR4.3: Alerts shall be configurable by time, event type, or stock performance.

3.1.5 User Management

-  FR5.1: The system shall allow users to sign up with email or OAuth (Google, LinkedIn).

-  FR5.2: Users shall have a profile page showing their saved stocks, predictions history, and alerts.

________________________________________

4\. External Interface Requirements

4.1 User Interfaces

-  Web App UI built with React and TailwindCSS

-  Mobile App UI optimized for Android/iOS

-  Interactive charts using libraries like Chart.js, D3.js, or Recharts

4.2 Hardware Interfaces

-  Standard devices: Desktop, Mobile, Tablet

4.3 Software Interfaces

-  Financial API integration (e.g., IEX Cloud, Alpha Vantage)

-  Machine Learning endpoints (FastAPI backend)

-  PostgreSQL or MongoDB for data storage

4.4 Communications Interfaces

-  HTTPS for all communications

-  RESTful APIs with token-based authentication (JWT)

________________________________________

5\. Nonfunctional Requirements

5.1 Performance

-  System must return query results within 1 second for UI, 2 seconds for predictions.

5.2 Scalability

-  Should support up to 100,000 concurrent users

5.3 Security

-  All data must be encrypted at rest and in transit

-  Users must authenticate with OAuth or email-based login

-  Role-based access for admin vs. user features

5.4 Usability

-  Novice users must be able to use the app effectively within 10 minutes

-  Glossary and walkthroughs must be included

5.5 Reliability

-  Uptime target: 99.9%

-  Backups of stock data and user data nightly

________________________________________

6\. Appendix

A. Assumptions and Dependencies

-  Reliable internet access for users

-  Accurate financial data from third-party APIs

-  ML predictions are probabilistic and not guaranteed

B. Future Enhancements

-  Integration with brokerage APIs (e.g., Robinhood, E*Trade)

-  Sentiment analysis from news and social media

-  Portfolio simulation and risk assessment tools
