import json
import subprocess
import sys

import time


# Get all city names from city_by_states dictionary
num_sys=3
rank=1


# Job roles

job_by_department = {
    # IT Related Departments First
    "IT Department": [
    "IT Manager",
    "IT Executive",
    "IT Officer",
    "IT Coordinator",
    "IT Administrator",
    "IT Analyst",
    "IT Consultant",
    "IT Specialist",
    "IT Engineer",
    "IT Technician",
    "IT Operations Manager",
    "IT Service Manager",
    "IT Asset Manager",
    "IT Helpdesk Executive",
    "IT Support Engineer",
    "Software Developer",
    "Software Engineer",
    "Junior Software Developer",
    "Senior Software Developer",
    "Software Programmer",
    "Application Developer",
    "Application Engineer",
    "Java Developer",
    "Python Developer",
    "PHP Developer",
    "Node.js Developer",
    ".NET Developer",
    "C++ Developer",
    "C# Developer",
    "Go Developer",
    "Ruby Developer",
    "Software Architect",
    "Technical Lead",
    "Engineering Manager",
    "Web Developer",
    "Junior Web Developer",
    "Senior Web Developer",
    "Website Developer",
    "PHP Web Developer",
    "WordPress Developer",
    "Shopify Developer",
    "Laravel Developer",
    "Django Developer",
    "Flask Developer",
    "MERN Stack Developer",
    "MEAN Stack Developer",
    "Web Application Developer",
    "Web Designer",
    "Webmaster",
    "Mobile App Developer",
    "Android Developer",
    "iOS Developer",
    "Flutter Developer",
    "React Native Developer",
    "Kotlin Developer",
    "Swift Developer",
    "Mobile Application Engineer",
    "Hybrid App Developer",
    "Mobile UI Developer",
    "Mobile App Tester",
    "Senior Mobile Developer",
    "Frontend Developer",
    "Frontend Engineer",
    "React Developer",
    "Angular Developer",
    "Vue.js Developer",
    "JavaScript Developer",
    "TypeScript Developer",
    "HTML CSS Developer",
    "UI Developer",
    "Web UI Developer",
    "Frontend Lead",
    "Senior Frontend Developer",
    "Backend Developer",
    "Backend Engineer",
    "API Developer",
    "Server Side Developer",
    "Java Backend Developer",
    "Python Backend Developer",
    "Node.js Backend Developer",
    "PHP Backend Developer",
    "Django Backend Developer",
    "Spring Boot Developer",
    "Database Backend Developer",
    "Backend Lead",
    "Senior Backend Developer",
    "Full Stack Developer",
    "Full Stack Engineer",
    "MERN Stack Developer",
    "MEAN Stack Developer",
    "Java Full Stack Developer",
    "Python Full Stack Developer",
    "PHP Full Stack Developer",
    ".NET Full Stack Developer",
    "React Full Stack Developer",
    "Angular Full Stack Developer",
    "Senior Full Stack Developer",
    "Full Stack Technical Lead",
    "DevOps Engineer",
    "DevOps Developer",
    "DevOps Architect",
    "Cloud DevOps Engineer",
    "AWS DevOps Engineer",
    "Azure DevOps Engineer",
    "CI CD Engineer",
    "Build and Release Engineer",
    "Site Reliability Engineer",
    "Infrastructure Engineer",
    "Platform Engineer",
    "Docker Engineer",
    "Kubernetes Engineer",
    "Cloud Engineer",
    "Cloud Architect",
    "Cloud Administrator",
    "Cloud Consultant",
    "AWS Engineer",
    "Azure Engineer",
    "Google Cloud Engineer",
    "Cloud Support Engineer",
    "Cloud Security Engineer",
    "Cloud Infrastructure Engineer",
    "Cloud Operations Engineer",
    "Cloud Migration Engineer",
    "Cloud Solution Architect",
    "Cyber Security Analyst",
    "Cyber Security Engineer",
    "Security Analyst",
    "Information Security Analyst",
    "SOC Analyst",
    "Security Engineer",
    "Ethical Hacker",
    "Penetration Tester",
    "Vulnerability Analyst",
    "Network Security Engineer",
    "Application Security Engineer",
    "Security Consultant",
    "Cyber Security Manager",
    "Network Administrator",
    "Network Engineer",
    "Network Support Engineer",
    "Network Technician",
    "Network Analyst",
    "LAN WAN Engineer",
    "Routing and Switching Engineer",
    "Firewall Engineer",
    "NOC Engineer",
    "Wireless Network Engineer",
    "Network Security Engineer",
    "Senior Network Administrator",
    "System Administrator",
    "Linux Administrator",
    "Windows Administrator",
    "Server Administrator",
    "System Engineer",
    "System Support Engineer",
    "Infrastructure Administrator",
    "VMware Administrator",
    "Active Directory Administrator",
    "Backup Administrator",
    "System Operations Engineer",
    "Database Administrator",
    "SQL DBA",
    "MySQL DBA",
    "PostgreSQL DBA",
    "Oracle DBA",
    "MongoDB Administrator",
    "Database Engineer",
    "Database Developer",
    "Data Warehouse Administrator",
    "Database Analyst",
    "Senior Database Administrator",
    "Data Scientist",
    "Junior Data Scientist",
    "Senior Data Scientist",
    "Data Science Engineer",
    "Applied Data Scientist",
    "Research Data Scientist",
    "NLP Data Scientist",
    "Computer Vision Scientist",
    "Statistical Analyst",
    "Predictive Modeling Analyst",
    "Data Science Manager",
    "Data Analyst",
    "Junior Data Analyst",
    "Senior Data Analyst",
    "Business Data Analyst",
    "Reporting Analyst",
    "MIS Analyst",
    "Excel Analyst",
    "SQL Analyst",
    "Data Visualization Analyst",
    "Operations Analyst",
    "Marketing Data Analyst",
    "Financial Data Analyst",
    "Business Intelligence Analyst",
    "BI Developer",
    "BI Engineer",
    "Power BI Developer",
    "Tableau Developer",
    "Looker Developer",
    "Data Visualization Developer",
    "BI Consultant",
    "BI Manager",
    "Reporting Developer",
    "Dashboard Developer",
    "AI Engineer",
    "AI Developer",
    "AI Researcher",
    "AI Scientist",
    "Generative AI Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "AI Consultant",
    "AI Product Manager",
    "AI Solution Architect",
    "Prompt Engineer",
    "AI Trainer",
    "Machine Learning Engineer",
    "ML Engineer",
    "Machine Learning Developer",
    "ML Scientist",
    "Deep Learning Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "MLOps Engineer",
    "ML Research Engineer",
    "Recommendation System Engineer",
    "Senior Machine Learning Engineer",
    "Quality Assurance Engineer",
    "QA Engineer",
    "QA Analyst",
    "QA Tester",
    "QA Lead",
    "QA Manager",
    "Quality Analyst",
    "Software Quality Analyst",
    "Test Engineer",
    "Test Lead",
    "Quality Assurance Specialist",
    "Software Tester",
    "Testing Engineer",
    "QA Tester",
    "Manual Tester",
    "Automation Tester",
    "Functional Tester",
    "Regression Tester",
    "Performance Tester",
    "Security Tester",
    "Mobile App Tester",
    "Web Application Tester",
    "Test Analyst",
    "Automation Tester",
    "Automation Test Engineer",
    "Selenium Tester",
    "Cypress Tester",
    "Playwright Tester",
    "API Automation Tester",
    "Performance Automation Tester",
    "Test Automation Architect",
    "QA Automation Engineer",
    "Automation QA Lead",
    "Manual Tester",
    "Manual Test Engineer",
    "QA Manual Tester",
    "Functional Tester",
    "Regression Tester",
    "UAT Tester",
    "Mobile Manual Tester",
    "Web Manual Tester",
    "Test Case Writer",
    "Bug Tester",
    "Quality Analyst",
    "IT Support Engineer",
    "IT Support Executive",
    "Desktop Support Engineer",
    "Helpdesk Support Executive",
    "Technical Support Engineer",
    "System Support Engineer",
    "Hardware Support Engineer",
    "Software Support Engineer",
    "Remote Support Engineer",
    "L1 Support Engineer",
    "L2 Support Engineer",
    "Technical Support Executive",
    "Technical Support Engineer",
    "Customer Technical Support",
    "Product Support Engineer",
    "Application Support Engineer",
    "Software Support Engineer",
    "Hardware Support Engineer",
    "Voice Technical Support",
    "Chat Technical Support",
    "L1 Technical Support",
    "L2 Technical Support",
    "Product Manager",
    "Associate Product Manager",
    "Senior Product Manager",
    "Product Owner",
    "Technical Product Manager",
    "Software Product Manager",
    "Product Analyst",
    "Product Consultant",
    "Product Lead",
    "Product Head",
    "Chief Product Officer",
    "Project Manager",
    "IT Project Manager",
    "Software Project Manager",
    "Technical Project Manager",
    "Project Coordinator",
    "Project Lead",
    "Scrum Master",
    "Agile Project Manager",
    "Delivery Manager",
    "Implementation Manager",
    "Project Director",
    "Program Manager",
    "Technical Program Manager",
    "Senior Program Manager",
    "Program Coordinator",
    "Program Lead",
    "Delivery Program Manager",
    "IT Program Manager",
    "Business Program Manager",
    "Program Director",
    "PMO Manager",
    "UI Designer",
    "UX Designer",
    "UI UX Designer",
    "Product Designer",
    "Interaction Designer",
    "Visual Designer",
    "User Researcher",
    "UX Researcher",
    "Wireframe Designer",
    "Prototype Designer",
    "Figma Designer",
    "Design Lead",
    "Game Developer",
    "Unity Developer",
    "Unreal Engine Developer",
    "Game Programmer",
    "Gameplay Programmer",
    "Game Designer",
    "Level Designer",
    "Game Artist",
    "3D Game Artist",
    "Game Tester",
    "Mobile Game Developer",
    "Blockchain Developer",
    "Blockchain Engineer",
    "Smart Contract Developer",
    "Solidity Developer",
    "Web3 Developer",
    "Crypto Developer",
    "Blockchain Architect",
    "DApp Developer",
    "NFT Developer",
    "Blockchain Consultant",
    "ERP Consultant",
    "ERP Developer",
    "ERP Administrator",
    "ERP Functional Consultant",
    "ERP Technical Consultant",
    "ERP Implementation Consultant",
    "ERP Support Executive",
    "ERP Analyst",
    "ERP Project Manager",
    "Odoo Developer",
    "Oracle ERP Consultant",
    "CRM Executive",
    "CRM Manager",
    "CRM Developer",
    "CRM Administrator",
    "CRM Analyst",
    "CRM Consultant",
    "Salesforce Developer",
    "Salesforce Administrator",
    "Zoho CRM Developer",
    "CRM Support Executive",
    "CRM Implementation Consultant",
    "SAP Consultant",
    "SAP Developer",
    "SAP ABAP Developer",
    "SAP Functional Consultant",
    "SAP Basis Administrator",
    "SAP FICO Consultant",
    "SAP MM Consultant",
    "SAP SD Consultant",
    "SAP HCM Consultant",
    "SAP Project Manager",
    "SAP Support Consultant",
    "IT Infrastructure Engineer",
    "Infrastructure Administrator",
    "Infrastructure Manager",
    "Infrastructure Architect",
    "Server Engineer",
    "Data Center Engineer",
    "Network Infrastructure Engineer",
    "Cloud Infrastructure Engineer",
    "Infrastructure Support Engineer",
    "IT Asset Executive",
    "IT Operations Executive",
    "IT Operations Engineer",
    "IT Operations Manager",
    "NOC Engineer",
    "Service Desk Engineer",
    "Application Operations Engineer",
    "Production Support Engineer",
    "IT Service Delivery Manager",
    "Operations Analyst",
    "IT Coordinator",
    "IT Security Analyst",
    "IT Security Engineer",
    "Information Security Officer",
    "Security Administrator",
    "Security Consultant",
    "Security Operations Analyst",
    "SOC Analyst",
    "Risk and Security Analyst",
    "Identity Access Management Analyst",
    "IT Security Manager",
    "Technical Writer",
    "Documentation Specialist",
    "API Documentation Writer",
    "Software Documentation Writer",
    "Content Documentation Executive",
    "User Manual Writer",
    "Technical Content Writer",
    "Knowledge Base Writer",
    "Instructional Writer",
    "Documentation Manager"
    ],

    # # Other Departments
    # "Administration": [
    #     "Admin Executive",
    #     "Admin Manager",
    #     "Office Administrator",
    #     "Office Assistant",
    #     "Administrative Assistant",
    #     "Front Office Executive",
    #     "Receptionist",
    #     "Office Coordinator",
    #     "Executive Assistant",
    #     "Personal Assistant",
    #     "Facility Administrator"
    # ],

    # "Accounts": [
    #     "Accountant",
    #     "Junior Accountant",
    #     "Senior Accountant",
    #     "Accounts Executive",
    #     "Accounts Assistant",
    #     "Accounts Manager",
    #     "Accounts Officer",
    #     "Billing Executive",
    #     "Bookkeeper",
    #     "Tally Operator",
    #     "Ledger Executive"
    # ],

    # "Finance": [
    #     "Finance Executive",
    #     "Finance Analyst",
    #     "Finance Manager",
    #     "Financial Analyst",
    #     "Financial Controller",
    #     "Budget Analyst",
    #     "Treasury Executive",
    #     "Investment Analyst",
    #     "Credit Analyst",
    #     "Finance Officer",
    #     "Chief Financial Officer"
    # ],

    # "Audit": [
    #     "Audit Executive",
    #     "Audit Assistant",
    #     "Internal Auditor",
    #     "External Auditor",
    #     "Senior Auditor",
    #     "Audit Manager",
    #     "Financial Auditor",
    #     "Compliance Auditor",
    #     "Stock Auditor",
    #     "Process Auditor",
    #     "Risk Auditor"
    # ],

    # "Taxation": [
    #     "Tax Executive",
    #     "Tax Consultant",
    #     "GST Executive",
    #     "Income Tax Executive",
    #     "Tax Analyst",
    #     "Tax Manager",
    #     "Direct Tax Consultant",
    #     "Indirect Tax Consultant",
    #     "Taxation Officer",
    #     "GST Accountant"
    # ],

    # "Human Resources": [
    #     "HR Executive",
    #     "HR Manager",
    #     "HR Generalist",
    #     "HR Assistant",
    #     "HR Officer",
    #     "HR Business Partner",
    #     "Employee Relations Executive",
    #     "HR Coordinator",
    #     "HR Operations Executive",
    #     "HR Head",
    #     "Chief Human Resources Officer"
    # ],

    # "Recruitment": [
    #     "Recruiter",
    #     "HR Recruiter",
    #     "IT Recruiter",
    #     "Non IT Recruiter",
    #     "Talent Acquisition Executive",
    #     "Talent Acquisition Specialist",
    #     "Recruitment Consultant",
    #     "Staffing Specialist",
    #     "Sourcing Specialist",
    #     "Recruitment Manager",
    #     "Campus Recruiter"
    # ],

    # "Training and Development": [
    #     "Training Executive",
    #     "Training Manager",
    #     "Corporate Trainer",
    #     "Learning and Development Executive",
    #     "L&D Manager",
    #     "Soft Skills Trainer",
    #     "Technical Trainer",
    #     "Process Trainer",
    #     "Product Trainer",
    #     "Instructional Designer"
    # ],

    # "Payroll": [
    #     "Payroll Executive",
    #     "Payroll Specialist",
    #     "Payroll Officer",
    #     "Payroll Manager",
    #     "Salary Processing Executive",
    #     "Compensation Executive",
    #     "Benefits Executive",
    #     "HR Payroll Executive",
    #     "Payroll Analyst"
    # ],

    # "Legal": [
    #     "Legal Executive",
    #     "Legal Officer",
    #     "Legal Advisor",
    #     "Legal Consultant",
    #     "Corporate Lawyer",
    #     "Company Secretary",
    #     "Contract Manager",
    #     "Legal Manager",
    #     "Compliance Lawyer",
    #     "Legal Associate"
    # ],

    # "Compliance": [
    #     "Compliance Executive",
    #     "Compliance Officer",
    #     "Compliance Analyst",
    #     "Compliance Manager",
    #     "Risk Compliance Officer",
    #     "Regulatory Compliance Executive",
    #     "Audit Compliance Executive",
    #     "KYC Compliance Officer",
    #     "Legal Compliance Manager"
    # ],

    # "Operations": [
    #     "Operations Executive",
    #     "Operations Manager",
    #     "Operations Coordinator",
    #     "Operations Analyst",
    #     "Operations Supervisor",
    #     "Process Executive",
    #     "Process Manager",
    #     "Branch Operations Manager",
    #     "General Manager Operations",
    #     "Chief Operating Officer"
    # ],

    # "Business Operations": [
    #     "Business Operations Executive",
    #     "Business Operations Manager",
    #     "Business Analyst",
    #     "Operations Analyst",
    #     "Business Process Analyst",
    #     "Business Coordinator",
    #     "Strategy Operations Manager",
    #     "Business Support Executive",
    #     "Business Operations Lead"
    # ],

    # "Sales": [
    #     "Sales Executive",
    #     "Sales Officer",
    #     "Sales Manager",
    #     "Sales Representative",
    #     "Sales Associate",
    #     "Sales Consultant",
    #     "Area Sales Manager",
    #     "Regional Sales Manager",
    #     "Sales Head",
    #     "Account Executive",
    #     "Key Account Manager"
    # ],

    # "Inside Sales": [
    #     "Inside Sales Executive",
    #     "Inside Sales Representative",
    #     "Inside Sales Manager",
    #     "Sales Development Representative",
    #     "Lead Generation Executive",
    #     "Telesales Executive",
    #     "B2B Sales Executive",
    #     "Pre Sales Executive",
    #     "Inside Sales Consultant"
    # ],

    # "Field Sales": [
    #     "Field Sales Executive",
    #     "Field Sales Officer",
    #     "Field Sales Manager",
    #     "Territory Sales Executive",
    #     "Area Sales Executive",
    #     "Business Sales Executive",
    #     "Sales Promoter",
    #     "Medical Representative",
    #     "Channel Sales Executive",
    #     "Door to Door Sales Executive"
    # ],

    # "Business Development": [
    #     "Business Development Executive",
    #     "Business Development Manager",
    #     "BD Executive",
    #     "BD Manager",
    #     "Partnership Manager",
    #     "Growth Manager",
    #     "Client Acquisition Executive",
    #     "Market Development Executive",
    #     "Business Development Associate",
    #     "Strategic Partnership Manager"
    # ],

    # "Marketing": [
    #     "Marketing Executive",
    #     "Marketing Manager",
    #     "Marketing Coordinator",
    #     "Marketing Officer",
    #     "Marketing Analyst",
    #     "Marketing Specialist",
    #     "Product Marketing Manager",
    #     "Growth Marketing Manager",
    #     "Campaign Manager",
    #     "Marketing Head"
    # ],

    # "Digital Marketing": [
    #     "Digital Marketing Executive",
    #     "Digital Marketing Manager",
    #     "SEO Executive",
    #     "SEO Specialist",
    #     "SEM Executive",
    #     "PPC Specialist",
    #     "Social Media Executive",
    #     "Google Ads Specialist",
    #     "Email Marketing Executive",
    #     "Performance Marketing Manager"
    # ],

    # "Content Marketing": [
    #     "Content Marketing Executive",
    #     "Content Marketing Manager",
    #     "Content Strategist",
    #     "Content Creator",
    #     "SEO Content Writer",
    #     "Blog Writer",
    #     "Social Media Content Executive",
    #     "Content Editor",
    #     "Brand Content Manager"
    # ],

    # "Brand Management": [
    #     "Brand Executive",
    #     "Brand Manager",
    #     "Assistant Brand Manager",
    #     "Brand Strategist",
    #     "Brand Marketing Manager",
    #     "Brand Communication Manager",
    #     "Brand Analyst",
    #     "Creative Brand Manager"
    # ],

    # "Public Relations": [
    #     "Public Relations Executive",
    #     "PR Executive",
    #     "PR Manager",
    #     "Media Relations Executive",
    #     "Corporate Communication Executive",
    #     "Communication Manager",
    #     "Press Officer",
    #     "Public Affairs Manager",
    #     "PR Consultant"
    # ],

    # "Customer Support": [
    #     "Customer Support Executive",
    #     "Customer Support Associate",
    #     "Customer Support Representative",
    #     "Customer Care Executive",
    #     "Customer Success Executive",
    #     "Support Specialist",
    #     "Chat Support Executive",
    #     "Email Support Executive",
    #     "Voice Support Executive",
    #     "Customer Support Manager"
    # ],

    # "Customer Service": [
    #     "Customer Service Executive",
    #     "Customer Service Associate",
    #     "Customer Service Representative",
    #     "Customer Service Manager",
    #     "Service Coordinator",
    #     "Client Service Executive",
    #     "Customer Care Officer",
    #     "Service Desk Executive",
    #     "Customer Experience Executive"
    # ],

    # "Client Relationship Management": [
    #     "Client Relationship Executive",
    #     "Client Relationship Manager",
    #     "Relationship Manager",
    #     "Client Success Manager",
    #     "Customer Relationship Manager",
    #     "Account Manager",
    #     "Key Account Manager",
    #     "Client Servicing Executive",
    #     "Client Coordinator"
    # ],

    # "Design": [
    #     "Designer",
    #     "Creative Designer",
    #     "Visual Designer",
    #     "Product Designer",
    #     "Design Executive",
    #     "Design Manager",
    #     "Design Lead",
    #     "Layout Designer",
    #     "Digital Designer",
    #     "Junior Designer"
    # ],

    # "Graphic Design": [
    #     "Graphic Designer",
    #     "Senior Graphic Designer",
    #     "Junior Graphic Designer",
    #     "Creative Graphic Designer",
    #     "Logo Designer",
    #     "Brand Designer",
    #     "Photoshop Designer",
    #     "Illustrator Designer",
    #     "Social Media Designer",
    #     "Print Designer"
    # ],

    # "Creative Design": [
    #     "Creative Designer",
    #     "Creative Head",
    #     "Creative Director",
    #     "Art Director",
    #     "Visual Designer",
    #     "Campaign Designer",
    #     "Advertising Designer",
    #     "Brand Creative Designer",
    #     "Creative Associate"
    # ],

    # "Animation": [
    #     "Animator",
    #     "2D Animator",
    #     "3D Animator",
    #     "Motion Graphics Designer",
    #     "Character Animator",
    #     "VFX Artist",
    #     "Animation Designer",
    #     "Storyboard Artist",
    #     "Maya Artist",
    #     "Blender Artist"
    # ],

    # "Video Editing": [
    #     "Video Editor",
    #     "Senior Video Editor",
    #     "Junior Video Editor",
    #     "Film Editor",
    #     "YouTube Video Editor",
    #     "Reel Editor",
    #     "Motion Video Editor",
    #     "Post Production Editor",
    #     "Video Production Executive"
    # ],

    # "Content Writing": [
    #     "Content Writer",
    #     "SEO Content Writer",
    #     "Blog Writer",
    #     "Article Writer",
    #     "Website Content Writer",
    #     "Creative Writer",
    #     "Content Editor",
    #     "Content Executive",
    #     "Content Manager",
    #     "Academic Content Writer"
    # ],

    # "Copywriting": [
    #     "Copywriter",
    #     "Creative Copywriter",
    #     "Marketing Copywriter",
    #     "Advertising Copywriter",
    #     "SEO Copywriter",
    #     "Brand Copywriter",
    #     "Social Media Copywriter",
    #     "Email Copywriter",
    #     "Senior Copywriter"
    # ],

    # "Research and Development": [
    #     "R&D Engineer",
    #     "R&D Executive",
    #     "Research Associate",
    #     "Research Analyst",
    #     "Research Scientist",
    #     "Product Researcher",
    #     "Development Engineer",
    #     "Innovation Manager",
    #     "R&D Manager",
    #     "Research Officer"
    # ],

    # "Engineering": [
    #     "Engineer",
    #     "Junior Engineer",
    #     "Senior Engineer",
    #     "Engineering Manager",
    #     "Engineering Supervisor",
    #     "Project Engineer",
    #     "Design Engineer",
    #     "Maintenance Engineer",
    #     "Service Engineer",
    #     "Site Engineer"
    # ],

    # "Mechanical Engineering": [
    #     "Mechanical Engineer",
    #     "Design Engineer Mechanical",
    #     "Production Engineer",
    #     "Maintenance Engineer",
    #     "HVAC Engineer",
    #     "Automobile Engineer",
    #     "Mechanical Design Engineer",
    #     "Plant Engineer",
    #     "Quality Engineer Mechanical"
    # ],

    # "Electrical Engineering": [
    #     "Electrical Engineer",
    #     "Electrical Design Engineer",
    #     "Electrical Maintenance Engineer",
    #     "Power Engineer",
    #     "Electrical Site Engineer",
    #     "Control Panel Engineer",
    #     "Electrical Supervisor",
    #     "Testing and Commissioning Engineer",
    #     "Electrical Project Engineer"
    # ],

    # "Electronics Engineering": [
    #     "Electronics Engineer",
    #     "Embedded Engineer",
    #     "PCB Design Engineer",
    #     "Electronics Design Engineer",
    #     "VLSI Engineer",
    #     "IoT Engineer",
    #     "Hardware Engineer",
    #     "Electronics Technician",
    #     "Testing Engineer Electronics"
    # ],

    # "Civil Engineering": [
    #     "Civil Engineer",
    #     "Site Engineer",
    #     "Structural Engineer",
    #     "Construction Engineer",
    #     "Planning Engineer",
    #     "Quantity Surveyor",
    #     "Civil Supervisor",
    #     "Highway Engineer",
    #     "Project Civil Engineer"
    # ],

    # "Production": [
    #     "Production Executive",
    #     "Production Engineer",
    #     "Production Manager",
    #     "Production Supervisor",
    #     "Line Supervisor",
    #     "Manufacturing Executive",
    #     "Process Engineer",
    #     "Production Planner",
    #     "Plant Production Manager"
    # ],

    # "Manufacturing": [
    #     "Manufacturing Engineer",
    #     "Manufacturing Manager",
    #     "Manufacturing Supervisor",
    #     "Plant Manager",
    #     "Machine Operator",
    #     "CNC Operator",
    #     "Assembly Operator",
    #     "Manufacturing Technician",
    #     "Industrial Engineer"
    # ],

    # "Maintenance": [
    #     "Maintenance Engineer",
    #     "Maintenance Technician",
    #     "Maintenance Manager",
    #     "Electrical Maintenance Engineer",
    #     "Mechanical Maintenance Engineer",
    #     "Plant Maintenance Engineer",
    #     "Service Technician",
    #     "Facility Maintenance Executive"
    # ],

    # "Plant Operations": [
    #     "Plant Operator",
    #     "Plant Manager",
    #     "Plant Supervisor",
    #     "Plant Engineer",
    #     "Plant Head",
    #     "Plant Maintenance Engineer",
    #     "Factory Manager",
    #     "Shift Incharge",
    #     "Production Plant Manager"
    # ],

    # "Quality Control": [
    #     "Quality Control Executive",
    #     "QC Inspector",
    #     "QC Engineer",
    #     "QC Analyst",
    #     "QC Manager",
    #     "Quality Inspector",
    #     "Lab QC Analyst",
    #     "Incoming Quality Inspector",
    #     "Final Quality Inspector"
    # ],

    # "Quality Management": [
    #     "Quality Manager",
    #     "Quality Executive",
    #     "Quality Engineer",
    #     "Quality Assurance Manager",
    #     "Quality Control Manager",
    #     "ISO Coordinator",
    #     "QMS Executive",
    #     "Quality Auditor",
    #     "Process Quality Manager"
    # ],

    # "Supply Chain": [
    #     "Supply Chain Executive",
    #     "Supply Chain Manager",
    #     "Supply Chain Analyst",
    #     "Supply Planner",
    #     "Demand Planner",
    #     "Logistics Coordinator",
    #     "Procurement Analyst",
    #     "Supply Chain Coordinator",
    #     "Inventory Planner"
    # ],

    # "Procurement": [
    #     "Procurement Executive",
    #     "Procurement Manager",
    #     "Procurement Officer",
    #     "Sourcing Executive",
    #     "Purchase Executive",
    #     "Vendor Development Executive",
    #     "Procurement Analyst",
    #     "Procurement Specialist"
    # ],

    # "Purchase": [
    #     "Purchase Executive",
    #     "Purchase Manager",
    #     "Purchase Officer",
    #     "Purchase Assistant",
    #     "Buying Executive",
    #     "Procurement Executive",
    #     "Vendor Coordinator",
    #     "Material Purchase Executive",
    #     "Purchase Analyst"
    # ],

    # "Vendor Management": [
    #     "Vendor Manager",
    #     "Vendor Management Executive",
    #     "Vendor Coordinator",
    #     "Vendor Development Executive",
    #     "Supplier Relationship Manager",
    #     "Procurement Vendor Manager",
    #     "Vendor Compliance Executive",
    #     "Vendor Onboarding Executive"
    # ],

    # "Inventory Management": [
    #     "Inventory Executive",
    #     "Inventory Manager",
    #     "Inventory Controller",
    #     "Inventory Analyst",
    #     "Stock Manager",
    #     "Stock Controller",
    #     "Store Keeper",
    #     "Warehouse Inventory Executive",
    #     "Material Controller"
    # ],

    # "Warehouse": [
    #     "Warehouse Executive",
    #     "Warehouse Manager",
    #     "Warehouse Supervisor",
    #     "Warehouse Associate",
    #     "Store Keeper",
    #     "Picker and Packer",
    #     "Dispatch Executive",
    #     "Warehouse Coordinator",
    #     "Warehouse Operations Manager"
    # ],

    # "Logistics": [
    #     "Logistics Executive",
    #     "Logistics Manager",
    #     "Logistics Coordinator",
    #     "Transport Coordinator",
    #     "Dispatch Executive",
    #     "Fleet Manager",
    #     "Shipping Executive",
    #     "Delivery Manager",
    #     "Logistics Supervisor"
    # ],

    # "Transportation": [
    #     "Transport Executive",
    #     "Transport Manager",
    #     "Fleet Manager",
    #     "Driver",
    #     "Delivery Driver",
    #     "Transport Coordinator",
    #     "Route Planner",
    #     "Vehicle Supervisor",
    #     "Transport Operations Manager"
    # ],

    # "Import Export": [
    #     "Import Export Executive",
    #     "Export Executive",
    #     "Import Executive",
    #     "Export Documentation Executive",
    #     "Customs Clearance Executive",
    #     "International Trade Executive",
    #     "Shipping Documentation Executive",
    #     "EXIM Manager",
    #     "Export Sales Executive"
    # ],

    # "Retail": [
    #     "Retail Sales Executive",
    #     "Retail Store Manager",
    #     "Retail Associate",
    #     "Store Executive",
    #     "Store Manager",
    #     "Cashier",
    #     "Retail Supervisor",
    #     "Retail Operations Manager",
    #     "Customer Sales Associate"
    # ],

    # "Merchandising": [
    #     "Merchandiser",
    #     "Retail Merchandiser",
    #     "Visual Merchandiser",
    #     "Fashion Merchandiser",
    #     "Buying Merchandiser",
    #     "Merchandising Manager",
    #     "Product Merchandiser",
    #     "Export Merchandiser"
    # ],

    # "Store Operations": [
    #     "Store Manager",
    #     "Store Executive",
    #     "Store Supervisor",
    #     "Store Keeper",
    #     "Store Operations Manager",
    #     "Retail Store Executive",
    #     "Inventory Store Executive",
    #     "Assistant Store Manager"
    # ],

    # "Ecommerce": [
    #     "Ecommerce Executive",
    #     "Ecommerce Manager",
    #     "Marketplace Executive",
    #     "Catalog Executive",
    #     "Product Listing Executive",
    #     "Ecommerce Operations Executive",
    #     "Online Sales Executive",
    #     "Ecommerce Analyst",
    #     "Ecommerce Coordinator"
    # ],

    # "Marketplace Operations": [
    #     "Marketplace Executive",
    #     "Marketplace Manager",
    #     "Amazon Marketplace Executive",
    #     "Flipkart Marketplace Executive",
    #     "Catalog Manager",
    #     "Product Listing Executive",
    #     "Marketplace Operations Analyst",
    #     "Seller Support Executive"
    # ],

    # "Healthcare": [
    #     "Healthcare Executive",
    #     "Healthcare Administrator",
    #     "Hospital Administrator",
    #     "Patient Care Executive",
    #     "Medical Officer",
    #     "Healthcare Manager",
    #     "Healthcare Coordinator",
    #     "Medical Records Executive",
    #     "Healthcare Consultant"
    # ],

    # "Medical": [
    #     "Doctor",
    #     "Medical Officer",
    #     "Resident Medical Officer",
    #     "Physician",
    #     "Surgeon",
    #     "Dentist",
    #     "Medical Consultant",
    #     "Medical Representative",
    #     "Medical Advisor",
    #     "Medical Coordinator"
    # ],

    # "Nursing": [
    #     "Nurse",
    #     "Staff Nurse",
    #     "Registered Nurse",
    #     "ICU Nurse",
    #     "Emergency Nurse",
    #     "OT Nurse",
    #     "Nursing Assistant",
    #     "Nursing Supervisor",
    #     "Head Nurse",
    #     "Home Care Nurse"
    # ],

    # "Pharmacy": [
    #     "Pharmacist",
    #     "Pharmacy Assistant",
    #     "Pharmacy Manager",
    #     "Clinical Pharmacist",
    #     "Hospital Pharmacist",
    #     "Retail Pharmacist",
    #     "Pharmacy Sales Executive",
    #     "Drug Safety Associate",
    #     "Pharma Executive"
    # ],

    # "Clinical Research": [
    #     "Clinical Research Associate",
    #     "Clinical Research Coordinator",
    #     "Clinical Data Manager",
    #     "Clinical Trial Assistant",
    #     "Medical Writer",
    #     "Clinical Project Manager",
    #     "Pharmacovigilance Associate",
    #     "Clinical Research Scientist"
    # ],

    # "Laboratory": [
    #     "Lab Technician",
    #     "Laboratory Assistant",
    #     "Lab Manager",
    #     "Medical Lab Technician",
    #     "Pathology Technician",
    #     "Quality Lab Analyst",
    #     "Research Lab Assistant",
    #     "Microbiologist",
    #     "Chemist"
    # ],

    # "Education": [
    #     "Teacher",
    #     "Lecturer",
    #     "Professor",
    #     "Academic Coordinator",
    #     "Education Counselor",
    #     "School Administrator",
    #     "Principal",
    #     "Curriculum Developer",
    #     "Education Consultant",
    #     "Tutor"
    # ],

    # "Teaching": [
    #     "Teacher",
    #     "Primary Teacher",
    #     "Secondary Teacher",
    #     "Math Teacher",
    #     "Science Teacher",
    #     "English Teacher",
    #     "Computer Teacher",
    #     "Subject Teacher",
    #     "Online Tutor",
    #     "Assistant Professor"
    # ],

    # "Training": [
    #     "Trainer",
    #     "Corporate Trainer",
    #     "Technical Trainer",
    #     "Soft Skills Trainer",
    #     "Sales Trainer",
    #     "Process Trainer",
    #     "Product Trainer",
    #     "Fitness Trainer",
    #     "Language Trainer",
    #     "Training Coordinator"
    # ],

    # "Academic Counselling": [
    #     "Academic Counselor",
    #     "Education Counselor",
    #     "Admission Counselor",
    #     "Career Counselor",
    #     "Student Counselor",
    #     "Course Counselor",
    #     "Academic Advisor",
    #     "Study Abroad Counselor"
    # ],

    # "Student Support": [
    #     "Student Support Executive",
    #     "Student Coordinator",
    #     "Student Success Executive",
    #     "Academic Support Executive",
    #     "Student Relationship Executive",
    #     "Student Service Executive",
    #     "Student Helpdesk Executive"
    # ],

    # "Hospitality": [
    #     "Hospitality Executive",
    #     "Hospitality Manager",
    #     "Guest Relations Executive",
    #     "Front Office Executive",
    #     "Hotel Receptionist",
    #     "Housekeeping Executive",
    #     "Food and Beverage Executive",
    #     "Banquet Manager"
    # ],

    # "Hotel Management": [
    #     "Hotel Manager",
    #     "Front Office Manager",
    #     "Receptionist",
    #     "Guest Relations Manager",
    #     "Housekeeping Manager",
    #     "Restaurant Manager",
    #     "Room Service Executive",
    #     "Hotel Operations Manager"
    # ],

    # "Travel and Tourism": [
    #     "Travel Consultant",
    #     "Travel Executive",
    #     "Tour Operator",
    #     "Tour Manager",
    #     "Ticketing Executive",
    #     "Visa Executive",
    #     "Travel Coordinator",
    #     "Holiday Consultant",
    #     "Tour Guide"
    # ],

    # "Food and Beverage": [
    #     "F&B Executive",
    #     "F&B Manager",
    #     "Restaurant Manager",
    #     "Chef",
    #     "Cook",
    #     "Waiter",
    #     "Barista",
    #     "Kitchen Supervisor",
    #     "Food Safety Officer",
    #     "Catering Manager"
    # ],

    # "Real Estate": [
    #     "Real Estate Executive",
    #     "Real Estate Agent",
    #     "Property Consultant",
    #     "Property Manager",
    #     "Sales Manager Real Estate",
    #     "Leasing Executive",
    #     "Real Estate Broker",
    #     "Site Sales Executive",
    #     "CRM Real Estate Executive"
    # ],

    # "Construction": [
    #     "Construction Manager",
    #     "Site Engineer",
    #     "Site Supervisor",
    #     "Project Engineer",
    #     "Civil Engineer",
    #     "Construction Worker",
    #     "Planning Engineer",
    #     "Quantity Surveyor",
    #     "Safety Officer",
    #     "Construction Project Manager"
    # ],

    # "Architecture": [
    #     "Architect",
    #     "Junior Architect",
    #     "Senior Architect",
    #     "Architectural Designer",
    #     "Landscape Architect",
    #     "Interior Architect",
    #     "Draftsman",
    #     "AutoCAD Designer",
    #     "BIM Architect"
    # ],

    # "Interior Design": [
    #     "Interior Designer",
    #     "Interior Design Consultant",
    #     "Interior Architect",
    #     "Furniture Designer",
    #     "Space Planner",
    #     "Modular Kitchen Designer",
    #     "AutoCAD Interior Designer",
    #     "3D Interior Visualizer"
    # ],

    # "Banking": [
    #     "Bank Officer",
    #     "Bank Manager",
    #     "Relationship Manager",
    #     "Branch Manager",
    #     "Cashier",
    #     "Credit Officer",
    #     "Loan Officer",
    #     "Operations Officer",
    #     "Banking Sales Executive",
    #     "KYC Officer"
    # ],

    # "Insurance": [
    #     "Insurance Advisor",
    #     "Insurance Agent",
    #     "Insurance Sales Executive",
    #     "Insurance Manager",
    #     "Claims Executive",
    #     "Underwriter",
    #     "Policy Servicing Executive",
    #     "Risk Insurance Analyst",
    #     "Bancassurance Executive"
    # ],

    # "Investment": [
    #     "Investment Analyst",
    #     "Investment Advisor",
    #     "Portfolio Manager",
    #     "Equity Research Analyst",
    #     "Mutual Fund Advisor",
    #     "Wealth Manager",
    #     "Financial Planner",
    #     "Stock Broker",
    #     "Investment Banking Analyst"
    # ],

    # "Risk Management": [
    #     "Risk Analyst",
    #     "Risk Manager",
    #     "Credit Risk Analyst",
    #     "Market Risk Analyst",
    #     "Operational Risk Manager",
    #     "Fraud Risk Analyst",
    #     "Risk Consultant",
    #     "Enterprise Risk Manager"
    # ],

    # "Loan and Credit": [
    #     "Loan Officer",
    #     "Credit Officer",
    #     "Credit Analyst",
    #     "Loan Sales Executive",
    #     "Mortgage Executive",
    #     "Loan Processor",
    #     "Collection Executive",
    #     "Credit Manager",
    #     "Loan Verification Executive"
    # ],

    # "Media": [
    #     "Media Executive",
    #     "Media Planner",
    #     "Media Manager",
    #     "Social Media Manager",
    #     "Content Producer",
    #     "News Producer",
    #     "Media Analyst",
    #     "Media Buyer",
    #     "Digital Media Executive"
    # ],

    # "Journalism": [
    #     "Journalist",
    #     "Reporter",
    #     "News Reporter",
    #     "Editor",
    #     "Sub Editor",
    #     "News Anchor",
    #     "Correspondent",
    #     "Photojournalist",
    #     "Content Journalist",
    #     "Investigative Journalist"
    # ],

    # "Publishing": [
    #     "Publishing Executive",
    #     "Editor",
    #     "Copy Editor",
    #     "Proofreader",
    #     "Publishing Manager",
    #     "Book Editor",
    #     "Editorial Assistant",
    #     "Layout Editor",
    #     "Publication Coordinator"
    # ],

    # "Event Management": [
    #     "Event Executive",
    #     "Event Manager",
    #     "Event Coordinator",
    #     "Wedding Planner",
    #     "Corporate Event Manager",
    #     "Event Planner",
    #     "Event Sales Executive",
    #     "Production Coordinator",
    #     "Venue Manager"
    # ],

    # "Security": [
    #     "Security Guard",
    #     "Security Officer",
    #     "Security Supervisor",
    #     "Security Manager",
    #     "Safety Officer",
    #     "Surveillance Operator",
    #     "CCTV Operator",
    #     "Security Incharge",
    #     "Bouncer"
    # ],

    # "Facility Management": [
    #     "Facility Executive",
    #     "Facility Manager",
    #     "Facility Supervisor",
    #     "Maintenance Supervisor",
    #     "Housekeeping Manager",
    #     "Admin Facility Executive",
    #     "Building Manager",
    #     "Facility Coordinator"
    # ],

    # "Housekeeping": [
    #     "Housekeeping Staff",
    #     "Housekeeping Executive",
    #     "Housekeeping Supervisor",
    #     "Housekeeping Manager",
    #     "Room Attendant",
    #     "Cleaner",
    #     "Janitor",
    #     "Housekeeping Attendant"
    # ],

    # "BPO": [
    #     "BPO Executive",
    #     "Customer Care Executive",
    #     "Voice Process Executive",
    #     "Non Voice Process Executive",
    #     "Process Associate",
    #     "Call Center Executive",
    #     "Team Leader BPO",
    #     "BPO Manager",
    #     "Quality Analyst BPO"
    # ],

    # "KPO": [
    #     "KPO Executive",
    #     "Research Analyst",
    #     "Data Analyst",
    #     "Business Research Analyst",
    #     "Financial Research Analyst",
    #     "Market Research Analyst",
    #     "Process Analyst",
    #     "Knowledge Analyst",
    #     "KPO Team Leader"
    # ],

    # "Telecalling": [
    #     "Telecaller",
    #     "Telecalling Executive",
    #     "Telesales Executive",
    #     "Customer Calling Executive",
    #     "Outbound Calling Executive",
    #     "Inbound Calling Executive",
    #     "Call Center Executive",
    #     "Lead Generation Executive",
    #     "Telemarketing Executive"
    # ],

    # "Data Entry": [
    #     "Data Entry Operator",
    #     "Data Entry Executive",
    #     "Computer Operator",
    #     "Typing Operator",
    #     "Back Office Data Entry Executive",
    #     "Excel Data Entry Operator",
    #     "Online Data Entry Operator",
    #     "Data Processing Executive"
    # ],

    # "Back Office": [
    #     "Back Office Executive",
    #     "Back Office Assistant",
    #     "Back Office Coordinator",
    #     "Operations Executive",
    #     "Documentation Executive",
    #     "Data Processing Executive",
    #     "Admin Support Executive",
    #     "MIS Executive"
    # ],

    # "Government": [
    #     "Government Officer",
    #     "Clerk",
    #     "Administrative Officer",
    #     "Public Service Officer",
    #     "Data Entry Operator",
    #     "Project Officer",
    #     "Field Officer",
    #     "Program Officer",
    #     "Government Consultant"
    # ],

    # "Public Sector": [
    #     "Public Sector Officer",
    #     "PSU Engineer",
    #     "Administrative Executive",
    #     "Public Relations Officer",
    #     "Public Sector Manager",
    #     "Operations Officer",
    #     "Public Policy Executive",
    #     "Field Coordinator"
    # ],

    # "NGO": [
    #     "NGO Coordinator",
    #     "Program Coordinator",
    #     "Program Manager",
    #     "Field Coordinator",
    #     "Fundraising Executive",
    #     "Social Worker",
    #     "Community Mobilizer",
    #     "Project Officer",
    #     "NGO Manager"
    # ],

    # "Social Work": [
    #     "Social Worker",
    #     "Community Worker",
    #     "Field Worker",
    #     "Counselor",
    #     "Program Officer",
    #     "Community Development Officer",
    #     "Welfare Officer",
    #     "Case Worker",
    #     "Outreach Worker"
    # ],

    # "Agriculture": [
    #     "Agriculture Officer",
    #     "Agronomist",
    #     "Farm Manager",
    #     "Agriculture Engineer",
    #     "Field Officer Agriculture",
    #     "Crop Advisor",
    #     "Soil Scientist",
    #     "Horticulture Officer",
    #     "Agriculture Sales Executive"
    # ],

    # "Food Processing": [
    #     "Food Processing Executive",
    #     "Food Technologist",
    #     "Food Safety Officer",
    #     "Production Executive Food",
    #     "Quality Analyst Food",
    #     "Food Processing Supervisor",
    #     "Packaging Executive",
    #     "Food Plant Manager"
    # ],

    # "Energy": [
    #     "Energy Engineer",
    #     "Renewable Energy Engineer",
    #     "Solar Engineer",
    #     "Energy Analyst",
    #     "Power Plant Engineer",
    #     "Energy Consultant",
    #     "Electrical Energy Engineer",
    #     "Wind Energy Engineer",
    #     "Energy Manager"
    # ],

    # "Oil and Gas": [
    #     "Oil and Gas Engineer",
    #     "Petroleum Engineer",
    #     "Drilling Engineer",
    #     "Pipeline Engineer",
    #     "Process Engineer",
    #     "Refinery Operator",
    #     "HSE Officer",
    #     "Oil Field Operator",
    #     "Gas Plant Operator"
    # ],

    # "Telecom": [
    #     "Telecom Engineer",
    #     "Telecom Technician",
    #     "RF Engineer",
    #     "Network Engineer Telecom",
    #     "Telecom Support Engineer",
    #     "Tower Technician",
    #     "Fiber Optic Technician",
    #     "Telecom Project Manager",
    #     "NOC Engineer Telecom"
    # ],

    # "Automobile": [
    #     "Automobile Engineer",
    #     "Automotive Technician",
    #     "Service Advisor",
    #     "Vehicle Mechanic",
    #     "AutoCAD Design Engineer",
    #     "Automobile Sales Executive",
    #     "Workshop Manager",
    #     "Quality Engineer Automobile",
    #     "Production Engineer Automobile"
    # ],

    # "Aviation": [
    #     "Aircraft Maintenance Engineer",
    #     "Cabin Crew",
    #     "Ground Staff",
    #     "Airport Operations Executive",
    #     "Airline Ticketing Executive",
    #     "Flight Attendant",
    #     "Pilot",
    #     "Aviation Security Officer",
    #     "Ramp Officer"
    # ],

    # "Marine": [
    #     "Marine Engineer",
    #     "Marine Technician",
    #     "Deck Officer",
    #     "Marine Surveyor",
    #     "Shipping Officer",
    #     "Port Operations Executive",
    #     "Marine Electrician",
    #     "Naval Architect",
    #     "Seafarer"
    # ],

    # "Shipping": [
    #     "Shipping Executive",
    #     "Shipping Manager",
    #     "Logistics Executive",
    #     "Export Documentation Executive",
    #     "Freight Forwarding Executive",
    #     "Cargo Executive",
    #     "Port Operations Executive",
    #     "Shipping Coordinator",
    #     "Customs Executive"
    # ],

    # "Sports": [
    #     "Sports Coach",
    #     "Sports Trainer",
    #     "Fitness Coach",
    #     "Sports Manager",
    #     "Sports Coordinator",
    #     "Athletic Trainer",
    #     "Sports Analyst",
    #     "Sports Event Manager",
    #     "Physical Education Teacher"
    # ],

    # "Fitness": [
    #     "Fitness Trainer",
    #     "Personal Trainer",
    #     "Gym Trainer",
    #     "Yoga Instructor",
    #     "Zumba Instructor",
    #     "Fitness Consultant",
    #     "Gym Manager",
    #     "Strength Coach",
    #     "Nutrition Coach"
    # ],

    # "Beauty and Wellness": [
    #     "Beautician",
    #     "Beauty Therapist",
    #     "Hair Stylist",
    #     "Makeup Artist",
    #     "Spa Therapist",
    #     "Wellness Consultant",
    #     "Salon Manager",
    #     "Nail Artist",
    #     "Skin Therapist"
    # ],

    # "Fashion": [
    #     "Fashion Designer",
    #     "Fashion Consultant",
    #     "Fashion Stylist",
    #     "Fashion Merchandiser",
    #     "Apparel Designer",
    #     "Textile Designer",
    #     "Fashion Buyer",
    #     "Pattern Maker",
    #     "Boutique Manager"
    # ],

    # "Textile": [
    #     "Textile Designer",
    #     "Textile Engineer",
    #     "Textile Merchandiser",
    #     "Fabric Manager",
    #     "Quality Analyst Textile",
    #     "Production Manager Textile",
    #     "Weaving Supervisor",
    #     "Dyeing Master",
    #     "Garment Technologist"
    # ],

    # "Jewellery": [
    #     "Jewellery Designer",
    #     "Jewellery Sales Executive",
    #     "Goldsmith",
    #     "Diamond Grader",
    #     "Jewellery Merchandiser",
    #     "Jewellery Store Manager",
    #     "CAD Jewellery Designer",
    #     "Gemologist",
    #     "Jewellery Production Executive"
    # ],

    # "Printing and Packaging": [
    #     "Printing Operator",
    #     "Packaging Executive",
    #     "Packaging Designer",
    #     "Print Production Executive",
    #     "Printing Supervisor",
    #     "Packaging Manager",
    #     "Prepress Operator",
    #     "Quality Inspector Packaging",
    #     "Graphic Prepress Designer"
    # ],

    # "Others": [
    #     "Intern",
    #     "Trainee",
    #     "Fresher",
    #     "Management Trainee",
    #     "Graduate Trainee",
    #     "Consultant",
    #     "Coordinator",
    #     "Executive",
    #     "Assistant",
    #     "Supervisor",
    #     "Manager",
    #     "Team Leader",
    #     "Freelancer",
    #     "Part Time Worker"
    # ]
}



# Cities by States



city_by_states = {
    "Major Cities": ["Delhi", "Gurugram", "Gurgaon", "Noida", "Greater Noida", 
                    "Faridabad", "Chandigarh", "Mohali", "Panchkula", "Bengaluru", 
                    "Bangalore", "Mysuru", "Mysore", "Mangaluru", "Mangalore", 
                    "Hubballi", "Hubli", "Belagavi", "Udupi", "Hyderabad", "Warangal",
                    "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli",
                    "Salem", "Vellore", "Tiruppur", "Erode", "Hosur",
                    "Chengalpattu", "Mumbai", "Pune", "Navi Mumbai", "Thane",
                    "Nagpur", "Nashik", "Aurangabad", "Kolhapur", "Solapur",
                    "Ahmedabad", "Gandhinagar", "Surat", "Vadodara", "Rajkot",
                    "Anand", "Vapi", "Bharuch", "Kochi", "Cochin",
                    "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kottayam",
                    "Ernakulam", "Kollam", "Indore", "Bhopal", "Gwalior",
                    "Jabalpur", "Jaipur", "Jodhpur", "Udaipur", "Kota",
                    "Ajmer", "Lucknow", "Kanpur", "Ghaziabad", "Meerut",
                    "Agra", "Varanasi", "Prayagraj", "Allahabad", "Bareilly",
                    "Kolkata", "Howrah", "Durgapur", "Siliguri", "Kharagpur",
                    "Asansol", "Bhubaneswar", "Cuttack", "Rourkela",
                    "Berhampur", "Visakhapatnam", "Vijayawada", "Guntur",
                    "Tirupati", "Kakinada", "Rajahmundry", "Nellore", "Patna",
                    "Ranchi", "Jamshedpur", "Dhanbad", "Bokaro Steel City",
                    "Raipur", "Bhilai", "Bilaspur", "Dehradun", "Roorkee",
                    "Haridwar", "Guwahati", "Shillong", "Imphal", "Agartala",
                    "Panaji", "Margao", "Vasco da Gama", "Porvorim"],
}

"""
    "Delhi NCR": ['Ballabgarh', 'Bhiwadi', 'Manesar', 'Jhajjar',
                  'Tauru', 'Khurja'],
    
    "Andhra Pradesh": [
        "Kurnool", "Kadapa", "Anantapur",
        "Eluru", "Ongole", "Machilipatnam", "Chittoor", "Hindupur",
        "Bhimavaram", "Tadepalligudem", "Proddatur", "Adoni", "Amalapuram",
        "Madanapalle", "Dharmavaram", "Markapur", "Nandyal", "Srikakulam",
        "Rajampet", "Peddapuram", "Rayachoti", "Bapatla",
        "Palnadu", "Kovur", "Tadipatri", "Punganur", "Chilakaluripet",
        "Sattenapalli", "Bobbili", "Peddapalli", "Anakapalle", "Addanki",
        "Chintapalli", "Peddagummadiv", "Brahmanapalli", "Tuni", "Tanuku",
        "Vinukonda", "Amadalavalasa", "Srikalahasti", "Mummidivaram",
    ],
    "Arunachal Pradesh": [
        "Itanagar", "Tawang", "Ziro", "Pasighat", "Roing",
        "Tezu", "Bomdila", "Naharlagun", "Changlang", "Seppa",
        "Yingkiong", "Namsai", "Hawai", "Aalo", "Raga", "Tali",
        "Joram", "Dirang", "Nirjuli", "Sangdupota", "Koloriang",
    ],
    "Assam": [
        "Silchar", "Dibrugarh", "Jorhat", "Nagaon",
        "Tinsukia", "Tezpur", "Bongaigaon", "North Lakhimpur",
        "Karimganj", "Goalpara", "Dhubri", "Haflong", "Sibsagar",
        "Sonari", "Nalbari", "Jorhat", "Barpeta", "Hojai", "Bajali",
        "Dibrugarh", "Dhemaji", "Morigaon", "Golaghat", "Kamrup", "Barpeta",
        "Mangaldoi", "Bilasipara", "Lakhimpur", "Charaideo", "Majuli",
        "Moran", "Darrang", "Hailakandi", "Haflong", "Tihu", "Bongaigaon",
    ],
    "Bihar": [
        "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia",
        "Darbhanga", "Begusarai", "Ara", "Katihar", "Munger",
        "Chhapra", "Saharsa", "Samastipur", "Bettiah", "Siwan",
        "Motihari", "Kishanganj", "Nalanda", "Buxar", "Nawada",
        "Lakhisarai", "Khagaria", "Sheikhpura", "Jamui", "Jahanabad",
        "Supaul", "Vaishali", "Rohtas", "Banka",
        "Bhabhua", "Chapra", "Buxar", "Chhapra", "Dehri", "Rajgir",
        "Patna City", "Phulwari Sharif", "Bihar Sharif",
    ],
    "Chhattisgarh": [
        "Korba", "Durg",
        "Rajnandgaon", "Jagdalpur", "Ambikapur", "Raigarh", "Mahasamund",
        "Kanker", "Dhamtari", "Dalli-Rajhara", "Champa", "Janjgir",
        "Bemetara", "Kondagaon", "Balod", "Raipur City", "Bijapur",
        "Narayanpur", "Balodabazar", "Mungeli", "Surguja", "Jashpur", "Kabirdham",
        "Surajpur", "Korba District", "Sarguja", "Dongargarh", "Kawardha",
    ],
    "Goa": [
        "Mapusa", "Ponda",
        "Bicholim", "Curchorem", "Sanguem", "Valpoi", "Quepem",
        "Canacona", "Sanquelim", "Cortalim", "Assagao", "Aldona",
        "Baga", "Calangute", "Candolim", "Anjuna", "Colva", "Benaulim",
        "Varca", "Majorda", "Navelim", "Raia", "Mormugao", "Verem",
        "Ribandar", "Sirsaim", "Taleigao", "Assagao",
    ],
    "Gujarat": [
        "Bhavnagar",
        "Jamnagar", "Junagadh", "Nadiad",
        "Morbi", "Porbandar", "Navsari", "Patan",
        "Godhra", "Mehsana", "Valsad", "Himmatnagar",
        "Dahod", "Bhuj", "Veraval", "Wankaner",
        "Surendranagar", "Unjha", "Rajpipla", "Visnagar", "Palanpur",
        "Modasa", "Kalol", "Viramgam", "Borsad", "Kheda", "Kadi",
        "Dholka", "Mansa", "Chhota Udepur", "Dahej", "Udhna", "Ankleshwar",
        "Navsari", "Tapi", "Daman", "Diu",
    ],
    "Haryana": [
        "Panipat", "Ambala", "Karnal",
        "Sonipat", "Rohtak", "Hisar", "Yamunanagar",
        "Bhiwani", "Bahadurgarh", "Sirsa", "Jind", "Kaithal",
        "Palwal", "Fatehabad", "Mahendragarh", "Rewari", "Narnaul",
        "Barwala", "Ratia", "Hansi", "Tosham", "Bawani Khera",
        "Pinjore", "Shahbad", "Nuh", "Samalkha", "Rohat",
    ],
    "Himachal Pradesh": [
        "Shimla", "Manali", "Dharamshala", "Mandi", "Kullu",
        "Chamba", "Solan", "Hamirpur", "Una",
        "Palampur", "Nahan", "Paonta Sahib", "Keylong", "Sundernagar",
        "Kangra", "Narkanda", "Kullu", "Bhuntar", "Arki", "Reckong Peo",
        "Jubbal", "Chintpurni", "Tissa", "Nagrota Surian", "Ghumarwin",
    ],
    "Jharkhand": [
        "Hazaribagh", "Deoghar", "Giridih", "Ramgarh", "Phusro",
        "Chakradharpur", "Gumla", "Lohardaga", "Chaibasa", "Seraikela",
        "Dumka", "Godda", "Pakur", "Koderma", "Simdega", "Latehar",
        "Khunti", "Sahibganj", "Palamu", "Chatra", "Bermo", "Jamtara",
        "Ramgarh", "Madhupur", "Barkagaon", "Mandar", "Tundi", "Tata Nagar",
    ],
    "Karnataka": [
        "Davanagere", "Ballari", "Shivamogga", "Tumakuru",
        "Mandya", "Chikkamagaluru", "Hassan", "Bijapur", "Bidar",
        "Gadag", "Chitradurga", "Raichur", "Karwar", "Hospet",
        "Kolar", "Bagalkot", "Gulbarga", "Vijayapura", "Hampi",
        "Sirsi", "Yadgir", "Bhadravati", "Sagar", "Channarayapatna",
        "Chikkaballapur", "Haveri", "Ramanagara", "Humnabad", "Puttur",
        "Karwar", "Karkala", "Alur", "Mudigere", "Kunigal", "Kadur",
    ],
    "Kerala": [
        "Kannur",
        "Alappuzha", "Palakkad", "Malappuram", "Muvattupuzha",
        "Vypin", "Varkala", "Pathanamthitta", "Punalur",
        "Kasaragod", "Payyanur", "Neyyattinkara", "Kalpetta", "Perumbavoor",
        "Thalassery", "Manjeri", "Kasargod", "Anchal", "Aluva",
        "Muvattupuzha", "Kanhangad", "Pattambi", "Perinthalmanna", "Sreekariyam",
        "Azhikkal", "Chalakudy", "Edappal", "Ponnani", "Edathala",
        "Irinjalakuda", "Kunnamkulam", "Changanassery", "Chirakkal",
    ],
    "Madhya Pradesh": [
        "Ujjain",
        "Sagar", "Ratlam", "Rewa", "Satna", "Dewas",
        "Chhindwara", "Murwara", "Vidisha", "Shivpuri", "Neemuch",
        "Khandwa", "Balaghat", "Mandla", "Damoh", "Betul", "Hoshangabad",
        "Shahdol", "Burhanpur", "Tikamgarh", "Panna", "Seoni", "Raisen",
        "Katni", "Alirajpur", "Anuppur", "Ashoknagar", "Mandsaur", "Rajgarh",
        "Narsinghpur", "Chhatarpur", "Shivpuri", "Datia", "Chhindwara",
        "Guna", "Pichhore", "Chhattarpur", "Dhar", "Jhabua",
    ],
    "Maharashtra": [
        "Amravati", "Sangli", "Latur", "Akola",
        "Jalgaon", "Nanded", "Ratnagiri", "Chandrapur", "Dhule",
        "Malegaon", "Ichalkaranji", "Jalna", "Ambarnath", "Badlapur",
        "Panvel", "Ulhasnagar", "Kalyan", "Dombivli", "Vasai",
        "Virar", "Satara", "Beed", "Alibag", "Baramati", "Shirdi",
        "Pandharpur", "Chiplun", "Osmanabad", "Gondia", "Hingoli",
        "Washim", "Yavatmal", "Karad", "Mahabaleshwar", "Palghar",
        "Talegaon", "Lonavala", "Vita", "Malkapur", "Dahanu", "Manmad",
        "Uran", "Sinnar", "Akluj", "Khamgaon", "Wai", "Pusad",
        "Shrirampur", "Sangamner", "Pathardi", "Digras", "Barshi",
        "Buldhana", "Kinwat", "Nandurbar", "Tumsar", "Gadchiroli",
        "Vijayapura", "Achalpur", "Murtijapur", "Rajgurunagar",
        "Parli", "Ambajogai", "Chandrapur", "Bhandara",
        "Wardha",
    ],
    "Manipur": [
        "Bishnupur", "Thoubal", "Churachandpur", "Kakching",
        "Jiribam", "Senapati", "Tamenglong", "Ukhrul", "Noney",
        "Chandel", "Kangpokpi", "Moirang", "Lamlai", "Tengnoupal",
    ],
    "Meghalaya": [
        "Tura", "Nongpoh", "Cherrapunji", "Jowai",
        "Mawkyrwat", "Bojan", "Nartiang", "Mairang", "Baghmara",
        "Williamnagar", "Resubelpara", "Nongstoin", "Pynursla",
        "Khasi Hills", "Garo Hills", "Ri Bhoi", "East Khasi Hills",
    ],
    "Mizoram": [
        "Aizawl", "Lunglei", "Serchhip", "Champhai", "Kolasib",
        "Mamit", "Saiha", "Lawngtlai", "Hnahthial", "Kolasib",
        "Khawzawl", "Vairengte", "Zohmun", "Tlabung", "Darlawn",
        "Ngopa", "Thenzawl", "Bungkawn", "Siaha",
    ],
    "Nagaland": [
        "Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha",
        "Mon", "Phek", "Zunhebuto", "Kiphire", "Longleng",
        "Tseminyu", "Chümoukedima", "Peren", "Jalukie",
        "Lotha", "Kohima Town", "Dimapur Town",
    ],
    "Odisha": [
        "Sambalpur",
        "Puri", "Balasore", "Baripada", "Bhadrak", "Angul",
        "Dhenkanal", "Jagatsinghpur", "Jeypore", "Khordha", "Nayagarh",
        "Balangir", "Bargarh", "Kendrapara", "Koraput", "Malkangiri",
        "Sundargarh", "Nimapara", "Khariar", "Rayagada", "Pattamundai",
        "Boudh", "Deogarh", "Ganjam", "Kendujhar", "Mayurbhanj",
    ],
    "Punjab": [
        "Ludhiana", "Amritsar", "Jalandhar", "Patiala",
        "Bathinda", "Hoshiarpur", "Pathankot", "Ferozepur",
        "Moga", "Rupnagar", "Kapurthala", "Faridkot", "Mansa",
        "Sri Muktsar Sahib", "Tarn Taran", "Fatehgarh Sahib", "Nawanshahr",
        "Zira", "Phagwara", "Sultanpur Lodhi", "Malerkotla",
        "Samrala", "Ajnala", "Dera Baba Nanak", "Moga", "Rampura Phul",
    ],
    "Rajasthan": [
        "Bikaner", "Alwar", "Bharatpur", "Sikar", "Jaisalmer",
        "Pali", "Churu", "Sawai Madhopur", "Nagaur", "Barmer",
        "Tonk", "Banswara", "Dungarpur", "Jhunjhunu", "Sri Ganganagar",
        "Hanumangarh", "Jhalawar", "Karauli", "Ratangarh", "Chittorgarh",
        "Rajsamand", "Kishangarh", "Beawar", "Mandawa", "Shahpura",
        "Merta City", "Pali", "Sirohi", "Bhilwara",
    ],
    "Sikkim": [
        "Gangtok", "Namchi", "Geyzing", "Mangan", "Rangpo",
        "Singtam", "Jorethang", "Rabong", "Sichey", "Tadong",
    ],
    "Tamil Nadu": [
        "Thoothukudi", "Dindigul", "Kanchipuram",
        "Tirunelveli", "Karur", "Vikramshila", "Pollachi",
        "Puducherry", "Nagercoil", "Ramanathapuram", "Tanjore", "Kumbakonam",
        "Virudhunagar", "Dharmapuri", "Perambalur", "Sivakasi", "Namakkal",
        "Cuddalore", "Arakkonam", "Nagapattinam", "Chidambaram",
        "Tiruvallur", "Bargur", "Ranipet",
    ],
    "Telangana": [
        "Nizamabad", "Karimnagar", "Ramagundam",
        "Khammam", "Mahbubnagar", "Mancherial", "Adilabad", "Miryalaguda",
        "Siddipet", "Jagtial", "Suryapet", "Nirmal", "Peddapalli",
        "Bhadrachalam", "Bhainsa", "Kothagudem", "Jagitial", "Wanaparthy",
        "Jangaon", "Nagarkurnool", "Medak", "Vikarabad", "Peddapalli",
    ],
    "Tripura": [
        "Kailashahar", "Dharmanagar", "Khowai",
        "Sabroom", "Belonia", "Bishalgarh", "Jirania", "Melaghar",
        "Sonamura", "Amarpur", "Madhupur", "Gakulpur", "Bagma",
    ],
    "Uttar Pradesh": [
        "Moradabad", "Aligarh",
        "Firozabad", "Mathura", "Shahjahanpur", "Rampur", "Saharanpur",
        "Muzaffarnagar", "Bijnor", "Jaunpur", "Raebareli", "Azamgarh",
        "Etawah", "Hapur", "Gorakhpur", "Sitapur",
        "Deoria", "Budaun", "Ballia", "Hardoi", "Amroha",
        "Basti", "Kushinagar", "Chandauli", "Jalaun", "Farrukhabad",
        "Sambhal", "Unnao", "Kanshiram Nagar", "Sonbhadra", "Shahabad",
        "Tanda", "Lakhimpur Kheri", "Mirzapur", "Pilibhit", "Raebareli",
    ],
    "Uttarakhand": [
        "Nainital", "Haldwani",
        "Rudrapur", "Almora", "Kashipur", "Pithoragarh", "Bageshwar",
        "Kotdwar", "Champawat", "Ranikhet", "Bharatpur", "Mussoorie",
        "Khatima", "Dhanaulti", "Tehri", "Lohaghat", "Kedarnath",
    ],
    "West Bengal": [
        "Darjeeling", "Hooghly", "Haldia", "Jalpaiguri",
        "Malda", "Raiganj", "Cooch Behar", "Medinipur", "Balurghat",
        "Alipurduar", "Suri", "Krishnanagar", "Tamluk", "Baharampur",
        "Chinsurah", "Rampurhat", "Santipur", "Kandi", "Bongaon",
        "Basirhat", "Habra", "Barrackpore", "Nabadwip", "Katwa",
        "Bolpur", "Uluberia", "Sainthia", "Jaynagar-Majilpur", "Budge Budge",
    ],
}
"""

#----------------------Original City By States----------------------------

# Original Cities by States



city_by_states_original = {
    "Delhi NCR": ['Delhi', 'Gurugram', 'Noida', 'Greater Noida',
                  'Ballabgarh', 'Bhiwadi', 'Manesar', 'Jhajjar',
                  'Tauru', 'Khurja'],
    
    "Andhra Pradesh": [
        "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool",
        "Tirupati", "Rajahmundry", "Kakinada", "Kadapa", "Anantapur",
        "Eluru", "Ongole", "Machilipatnam", "Chittoor", "Hindupur",
        "Bhimavaram", "Tadepalligudem", "Proddatur", "Adoni", "Amalapuram",
        "Madanapalle", "Dharmavaram", "Markapur", "Nandyal", "Srikakulam",
        "Rajampet", "Peddapuram", "Rayachoti", "Bapatla",
        "Nellore", "Palnadu", "Kovur", "Tadipatri", "Punganur", "Chilakaluripet",
        "Sattenapalli", "Bobbili", "Peddapalli", "Anakapalle", "Addanki",
        "Chintapalli", "Peddagummadiv", "Brahmanapalli", "Tuni", "Tanuku",
        "Vinukonda", "Amadalavalasa", "Srikalahasti", "Mummidivaram",
    ],
    "Arunachal Pradesh": [
        "Itanagar", "Tawang", "Ziro", "Pasighat", "Roing",
        "Tezu", "Bomdila", "Naharlagun", "Changlang", "Seppa",
        "Yingkiong", "Namsai", "Hawai", "Aalo", "Raga", "Tali", 
        "Joram", "Dirang", "Nirjuli", "Sangdupota", "Koloriang",
    ],
    "Assam": [
        "Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon",
        "Tinsukia", "Tezpur", "Bongaigaon", "North Lakhimpur",
        "Karimganj", "Goalpara", "Dhubri", "Haflong", "Sibsagar",
        "Sonari", "Nalbari", "Jorhat", "Barpeta", "Hojai", "Bajali",
        "Dibrugarh", "Dhemaji", "Morigaon", "Golaghat", "Kamrup", "Barpeta",
        "Mangaldoi", "Bilasipara", "Lakhimpur", "Charaideo", "Majuli",
        "Moran", "Darrang", "Hailakandi", "Haflong", "Tihu", "Bongaigaon",
    ],
    "Bihar": [
        "Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia",
        "Darbhanga", "Begusarai", "Ara", "Katihar", "Munger",
        "Chhapra", "Saharsa", "Samastipur", "Bettiah", "Siwan",
        "Motihari", "Kishanganj", "Nalanda", "Buxar", "Nawada",
        "Lakhisarai", "Khagaria", "Sheikhpura", "Jamui", "Jahanabad",
        "Supaul", "Vaishali", "Rohtas", "Aurangabad", "Banka",
        "Bhabhua", "Chapra", "Buxar", "Chhapra", "Dehri", "Rajgir",
        "Patna City", "Phulwari Sharif", "Bihar Sharif",
    ],
    "Chhattisgarh": [
        "Raipur", "Bhilai", "Bilaspur", "Korba", "Durg",
        "Rajnandgaon", "Jagdalpur", "Ambikapur", "Raigarh", "Mahasamund",
        "Kanker", "Dhamtari", "Dalli-Rajhara", "Champa", "Janjgir",
        "Bemetara", "Kondagaon", "Balod", "Raipur City", "Bijapur",
        "Narayanpur", "Balodabazar", "Mungeli", "Surguja", "Jashpur", "Kabirdham",
        "Surajpur", "Korba District", "Sarguja", "Dongargarh", "Kawardha", 
    ],
    "Goa": [
        "Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda",
        "Bicholim", "Curchorem", "Sanguem", "Valpoi", "Quepem",
        "Canacona", "Sanquelim", "Cortalim", "Assagao", "Aldona",
        "Baga", "Calangute", "Candolim", "Anjuna", "Colva", "Benaulim",
        "Varca", "Majorda", "Navelim", "Raia", "Mormugao", "Verem",
        "Ribandar", "Sirsaim", "Taleigao", "Porvorim", "Assagao",
    ],
    "Gujarat": [
        "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
        "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Nadiad",
        "Morbi", "Porbandar", "Navsari", "Bharuch", "Patan",
        "Godhra", "Mehsana", "Vapi", "Valsad", "Himmatnagar",
        "Dahod", "Bhuj", "Veraval", "Wankaner", "Gandhinagar",
        "Surendranagar", "Unjha", "Rajpipla", "Visnagar", "Palanpur",
        "Modasa", "Kalol", "Viramgam", "Borsad", "Kheda", "Kadi", 
        "Dholka", "Mansa", "Chhota Udepur", "Dahej", "Udhna", "Ankleshwar", 
        "Navsari", "Tapi", "Daman", "Diu",
    ],
    "Haryana": [
        "Gurgaon", "Faridabad", "Panipat", "Ambala", "Karnal",
        "Sonipat", "Rohtak", "Hisar", "Yamunanagar", "Panchkula",
        "Bhiwani", "Bahadurgarh", "Sirsa", "Jind", "Kaithal",
        "Palwal", "Fatehabad", "Mahendragarh", "Rewari", "Narnaul",
        "Barwala", "Ratia", "Hansi", "Tosham", "Bawani Khera", 
        "Pinjore", "Shahbad", "Nuh", "Samalkha", "Rohat",
    ],
    "Himachal Pradesh": [
        "Shimla", "Manali", "Dharamshala", "Mandi", "Kullu",
        "Chamba", "Solan", "Bilaspur", "Hamirpur", "Una",
        "Palampur", "Nahan", "Paonta Sahib", "Keylong", "Sundernagar",
        "Kangra", "Narkanda", "Kullu", "Bhuntar", "Arki", "Reckong Peo",
        "Jubbal", "Chintpurni", "Tissa", "Nagrota Surian", "Ghumarwin",
    ],
    "Jharkhand": [
        "Ranchi", "Jamshedpur", "Dhanbad", "Bokaro Steel City",
        "Hazaribagh", "Deoghar", "Giridih", "Ramgarh", "Phusro",
        "Chakradharpur", "Gumla", "Lohardaga", "Chaibasa", "Seraikela",
        "Dumka", "Godda", "Pakur", "Koderma", "Simdega", "Latehar",
        "Khunti", "Sahibganj", "Palamu", "Chatra", "Bermo", "Jamtara",
        "Ramgarh", "Madhupur", "Barkagaon", "Mandar", "Tundi", "Tata Nagar",
    ],
    "Karnataka": [
        "Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi",
        "Davanagere", "Ballari", "Shivamogga", "Tumakuru", "Udupi",
        "Mandya", "Chikkamagaluru", "Hassan", "Bijapur", "Bidar",
        "Gadag", "Chitradurga", "Raichur", "Karwar", "Hospet",
        "Kolar", "Bagalkot", "Gulbarga", "Hubli", "Vijayapura", "Hampi",
        "Sirsi", "Yadgir", "Bhadravati", "Sagar", "Channarayapatna", 
        "Chikkaballapur", "Haveri", "Ramanagara", "Humnabad", "Puttur", 
        "Karwar", "Karkala", "Alur", "Mudigere", "Kunigal", "Kadur",
    ],
    "Kerala": [
        "Thiruvananthapuram", "Kochi", "Kozhikode", "Kannur", "Kottayam",
        "Alappuzha", "Palakkad", "Thrissur", "Malappuram", "Muvattupuzha",
        "Vypin", "Varkala", "Pathanamthitta", "Ernakulam", "Punalur",
        "Kasaragod", "Payyanur", "Neyyattinkara", "Kalpetta", "Perumbavoor",
        "Thalassery", "Manjeri", "Kasargod", "Kollam", "Anchal", "Aluva",
        "Muvattupuzha", "Kanhangad", "Pattambi", "Perinthalmanna", "Sreekariyam",
        "Azhikkal", "Chalakudy", "Edappal", "Kollam", "Ponnani", "Edathala",
        "Cochin", "Irinjalakuda", "Kunnamkulam", "Changanassery", "Chirakkal",
    ],
    "Madhya Pradesh": [
        "Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain",
        "Sagar", "Ratlam", "Rewa", "Satna", "Dewas",
        "Chhindwara", "Murwara", "Vidisha", "Shivpuri", "Neemuch",
        "Khandwa", "Balaghat", "Mandla", "Damoh", "Betul", "Hoshangabad",
        "Shahdol", "Burhanpur", "Tikamgarh", "Panna", "Seoni", "Raisen",
        "Katni", "Alirajpur", "Anuppur", "Ashoknagar", "Mandsaur", "Rajgarh",
        "Narsinghpur", "Chhatarpur", "Shivpuri", "Datia", "Chhindwara", 
        "Bhilai", "Guna", "Pichhore", "Chhattarpur", "Dhar", "Jhabua",
    ],
    "Maharashtra": [
        "Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", 
        "Solapur", "Kolhapur", "Amravati", "Sangli", "Latur", "Akola", 
        "Jalgaon", "Nanded", "Ratnagiri", "Chandrapur", "Dhule", 
        "Malegaon", "Ichalkaranji", "Jalna", "Ambarnath", "Badlapur", 
        "Panvel", "Ulhasnagar", "Kalyan", "Dombivli", "Vasai", 
        "Virar", "Satara", "Beed", "Alibag", "Baramati", "Shirdi", 
        "Pandharpur", "Chiplun", "Osmanabad", "Gondia", "Hingoli", 
        "Washim", "Yavatmal", "Karad", "Mahabaleshwar", "Palghar", 
        "Talegaon", "Lonavala", "Vita", "Malkapur", "Dahanu", "Manmad", 
        "Uran", "Sinnar", "Akluj", "Khamgaon", "Wai", "Pusad", 
        "Shrirampur", "Sangamner", "Pathardi", "Digras", "Barshi", 
        "Buldhana", "Kinwat", "Nandurbar", "Tumsar", "Gadchiroli", 
        "Vijayapura", "Achalpur", "Murtijapur", "Rajgurunagar", 
        "Parli", "Ambajogai", "Chandrapur", "Nagpur", "Bhandara", 
        "Wardha", "Navi Mumbai", "Aurangabad",
    ],
    "Manipur": [
        "Imphal", "Bishnupur", "Thoubal", "Churachandpur", "Kakching",
        "Jiribam", "Senapati", "Tamenglong", "Ukhrul", "Noney", 
        "Chandel", "Kangpokpi", "Moirang", "Lamlai", "Tengnoupal",
    ],
    "Meghalaya": [
        "Shillong", "Tura", "Nongpoh", "Cherrapunji", "Jowai", 
        "Mawkyrwat", "Bojan", "Nartiang", "Mairang", "Baghmara", 
        "Williamnagar", "Resubelpara", "Nongstoin", "Pynursla", 
        "Khasi Hills", "Garo Hills", "Ri Bhoi", "East Khasi Hills",
    ],
    "Mizoram": [
        "Aizawl", "Lunglei", "Serchhip", "Champhai", "Kolasib", 
        "Mamit", "Saiha", "Lawngtlai", "Hnahthial", "Kolasib", 
        "Khawzawl", "Vairengte", "Zohmun", "Tlabung", "Darlawn", 
        "Ngopa", "Thenzawl", "Bungkawn", "Siaha",
    ],
    "Nagaland": [
        "Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha", 
        "Mon", "Phek", "Zunheboto", "Kiphire", "Longleng", 
        "Tseminyu", "Chümoukedima", "Peren", "Jalukie", 
        "Lotha", "Kohima Town", "Dimapur Town",
    ],
    "Odisha": [
        "Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur",
        "Puri", "Balasore", "Baripada", "Bhadrak", "Angul",
        "Dhenkanal", "Jagatsinghpur", "Jeypore", "Khordha", "Nayagarh",
        "Balangir", "Bargarh", "Kendrapara", "Koraput", "Malkangiri",
        "Sundargarh", "Nimapara", "Khariar", "Rayagada", "Pattamundai",
        "Boudh", "Deogarh", "Ganjam", "Kendujhar", "Mayurbhanj",
    ],
    "Punjab": [
        "Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala",
        "Bathinda", "Hoshiarpur", "Mohali", "Pathankot", "Ferozepur",
        "Moga", "Rupnagar", "Kapurthala", "Faridkot", "Mansa", 
        "Sri Muktsar Sahib", "Tarn Taran", "Fatehgarh Sahib", "Nawanshahr",
        "Zira", "Phagwara", "Sultanpur Lodhi", "Malerkotla", 
        "Samrala", "Ajnala", "Dera Baba Nanak", "Moga", "Rampura Phul",
    ],
    "Rajasthan": [
        "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer",
        "Bikaner", "Alwar", "Bharatpur", "Sikar", "Jaisalmer",
        "Pali", "Churu", "Sawai Madhopur", "Nagaur", "Barmer",
        "Tonk", "Banswara", "Dungarpur", "Jhunjhunu", "Sri Ganganagar",
        "Hanumangarh", "Jhalawar", "Karauli", "Ratangarh", "Chittorgarh",
        "Rajsamand", "Kishangarh", "Beawar", "Mandawa", "Shahpura", 
        "Merta City", "Pali", "Sirohi", "Kota", "Bhilwara", 
    ],
    "Sikkim": [
        "Gangtok", "Namchi", "Geyzing", "Mangan", "Rangpo",
        "Singtam", "Jorethang", "Rabong", "Sichey", "Tadong",
    ],
    "Tamil Nadu": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
        "Vellore", "Tiruppur", "Thoothukudi", "Dindigul", "Kanchipuram",
        "Tirunelveli", "Karur", "Erode", "Vikramshila", "Pollachi",
        "Puducherry", "Nagercoil", "Ramanathapuram", "Tanjore", "Kumbakonam",
        "Virudhunagar", "Dharmapuri", "Perambalur", "Sivakasi", "Namakkal",
        "Cuddalore", "Arakkonam", "Nagapattinam", "Vellore", "Chidambaram",
        "Tiruvallur", "Hosur", "Bargur", "Chengalpattu", "Ranipet", 
    ],
    "Telangana": [
        "Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Ramagundam",
        "Khammam", "Mahbubnagar", "Mancherial", "Adilabad", "Miryalaguda",
        "Siddipet", "Jagtial", "Suryapet", "Nirmal", "Peddapalli",
        "Bhadrachalam", "Bhainsa", "Kothagudem", "Jagitial", "Wanaparthy",
        "Jangaon", "Nagarkurnool", "Medak", "Vikarabad", "Peddapalli",
    ],
    "Tripura": [
        "Agartala", "Udaipur", "Kailashahar", "Dharmanagar", "Khowai",
        "Sabroom", "Belonia", "Bishalgarh", "Jirania", "Melaghar",
        "Sonamura", "Amarpur", "Madhupur", "Gakulpur", "Bagma",
    ],
    "Uttar Pradesh": [
        "Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut",
        "Allahabad", "Bareilly", "Ghaziabad", "Moradabad", "Aligarh",
        "Firozabad", "Mathura", "Shahjahanpur", "Rampur", "Saharanpur",
        "Muzaffarnagar", "Bijnor", "Jaunpur", "Raebareli", "Azamgarh",
        "Prayagraj", "Etawah", "Hapur", "Gorakhpur", "Sitapur",
        "Deoria", "Budaun", "Ballia", "Hardoi", "Amroha",
        "Basti", "Kushinagar", "Chandauli", "Jalaun", "Farrukhabad",
        "Sambhal", "Unnao", "Kanshiram Nagar", "Sonbhadra", "Shahabad",
        "Tanda", "Lakhimpur Kheri", "Mirzapur", "Pilibhit", "Raebareli",
    ],
    "Uttarakhand": [
        "Dehradun", "Haridwar", "Roorkee", "Nainital", "Haldwani",
        "Rudrapur", "Almora", "Kashipur", "Pithoragarh", "Bageshwar",
        "Kotdwar", "Champawat", "Ranikhet", "Bharatpur", "Mussoorie",
        "Khatima", "Dhanaulti", "Tehri", "Lohaghat", "Kedarnath",
    ],
    "West Bengal": [
        "Kolkata", "Howrah", "Asansol", "Durgapur", "Siliguri",
        "Darjeeling", "Hooghly", "Kharagpur", "Haldia", "Jalpaiguri",
        "Malda", "Raiganj", "Cooch Behar", "Medinipur", "Balurghat",
        "Alipurduar", "Suri", "Krishnanagar", "Tamluk", "Baharampur",
        "Chinsurah", "Rampurhat", "Santipur", "Kandi", "Bongaon",
        "Basirhat", "Habra", "Barrackpore", "Nabadwip", "Katwa",
        "Bolpur", "Uluberia", "Sainthia", "Jaynagar-Majilpur", "Budge Budge",
    ],
}



def check_state_city(input_city,state,threshold):
    for city in city_by_states_original[state]:
        if is_same(input_city,city,threshold):
            return True
    return False
    


def city_to_state(input_city,threshold=1):
    for state in city_by_states_original:
        if check_state_city(input_city,state,threshold):
            return state
    return 'Other'









#-------------------------NEXT SECTION-------------------------------------

# Lenestein word matching algorithm

from Levenshtein import distance as levenshtein_distance

def is_same(input_word, correct_word, threshold = 1):
    """
    Check if input_word has minor spelling mistakes compared to correct_word.
    Ignores case sensitivity and allows for small errors.

    Args:
        input_word (str): Word to be checked.
        correct_word (str): The correct reference word.
        threshold (int): Maximum allowed edit distance to consider words similar.

    Returns:
        bool: True if input_word is nearly the same as correct_word, False otherwise.
    """
    # Convert both words to lowercase to make comparison case insensitive
    input_word = str(input_word).lower()
    correct_word = str(correct_word).lower()
    
    # Calculate the Levenshtein distance
    distance = levenshtein_distance(input_word, correct_word)
    
    # Return True if the distance is within the allowed threshold
    return distance <= threshold


# Example usage
#print(is_same("hello", "Hello"))  # True (case difference)
#print(is_same("helllo", "hello"))  # True (1 letter extra)
#print(is_same("helo", "hello"))    # True (1 letter missing)
#print(is_same("hllo", "hello"))    # True (1 letter replaced)
#print(is_same("heallo", "hello"))  # False (too many differences)


langs = ["marathi", "kannada", "telugu", "english", "tamil",
         "bengali", "malayalam",]


city_by_langs = {
    "marathi": [
        "Mumbai", "Bombay", "Bambai", "Bumbai", "Aamchi Mumbai", "Mayanagari", "Maha Mumbai", 
        "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", 
        "Kolhapur", "Sangli", "Amravati", "Akola", "Latur", "Jalgaon", 
        "Parbhani", "Bhiwandi", "Nanded", "Ahmednagar", "Chandrapur", 
        "Dhule", "Malegaon", "Ichalkaranji", "Jalna", "Ambarnath", 
        "Badlapur", "Panvel", "Ulhasnagar", "Kalyan", "Dombivli", 
        "Vasai", "Virar", "Ratnagiri", "Wardha", "Beed", "Satara", 
        "Alibag", "Baramati", "Shirdi", "Pandharpur", "Chiplun", 
        "Osmanabad", "Gondia", "Hingoli", "Washim", "Yavatmal", 
        "Karad", "Mahabaleshwar", "Palghar", "Talegaon", "Lonavala", 
        "Vita", "Malkapur", "Dahanu", "Manmad", "Uran", "Sinnar", 
        "Akluj", "Khamgaon", "Wai", "Pusad", "Shrirampur", "Sangamner", 
        "Pathardi", "Digras", "Barshi", "Buldhana", "Kinwat", "Nandurbar", 
        "Tumsar", "Gadchiroli", "Vijayapura", "Achalpur", 
        "Murtijapur", "Rajgurunagar", "Parli", "Ambajogai",
    ],

    "kannada": [
        "Bangalore", "Bengaluru", "Bangaluru", "Bangalore City", "Bangalore Urban",
        "Bangalore Rural", "Bengalooru", "Namma Bengaluru", "Silicon Valley of India",
        "Garden City", "Tech City", "Startup Hub of India", "Karnataka Capital",
        "Bangalore Metro", "Bengaluru City", "Kempegowda City", "Bangalore IT Hub", "BLR",
        "Bangalore South", "Bangalore North", "Bangalore East", "Bangalore West",
        "Bangalore Central", "B'lore", "BGL", "Bangalor", "Bangalorean", "Bengaluru Nagara",
        "Bangalore Mega City", "Bangalore Metro City", "Namma Ooru Bengaluru",
        "Bengaluru Tech City",
        "Bagalkot", "Mahalingpur", "Terdal", "Jamkhandi", "Rabkavi Banhatti", "Bilgi", "Mudhol", "Kerur", "Badami",
        "Guledgudda", "Hungund", "Ilkal", "Anekal", "Nelamangala", "Dod Ballapur", "Vijayapura",
        "Devanahalli", "Hosakote", "Belgaum", "Nipani", "Sadalgi", "Athani", "Ramdurg", "Saundatti-Yellamma",
        "Bail Hongal", "Khanapur", "Mudalgi", "Gokak", "Hukeri", "Sankeshwar", "Chikodi", "Raibag", "Yellapur",
        "Mundgod", "Sirsi", "Dandeli", "Karwar", "Ankola", "Kumta", "Siddapur", "Honavar", "Bhatkal", "Mangalore",
        "Ullal", "Moodbidri", "Bantval", "Puttur", "Sullia", "Karkal", "Udupi", "Kundapura", "Saligram", "Kaup",
        "Kota", "Hebri", "Byndoor", "Chikkaballapur", "Chintamani", "Sidlaghatta", "Gauribidanur", "Bagepalli",
        "Chikkamagaluru", "Tarikere", "Kadur", "Birur", "Koppa", "Sringeri", "Mudigere", "Ajjampur", "Chitradurga",
        "Hiriyur", "Hosdurga", "Holalkere", "Molakalmuru", "Davanagere", "Harihar", "Honnali", "Jagalur",
        "Harapanahalli", "Hubli-Dharwad", "Navalgund", "Kalghatgi", "Gadag-Betigeri", "Nargund", "Mundargi", "Ron",
        "Shahabad", "Chitapur", "Sedam", "Yadgir", "Gurmatkal", "Shorapur", "Bidar", "Basavakalyan", "Bhalki",
        "Humnabad", "Hospet", "Kampli", "Kotturu", "Sandur", "Siruguppa", "Kudligi", "Koppal", "Gangavathi",
        "Kushtagi", "Yelbarga", "Raichur", "Manvi", "Sindhnur", "Lingsugur", "Devadurga", "Ramanagara",
        "Channapatna", "Kanakapura", "Magadi", "Mysore", "Nanjangud", "Tirumakudalu Narasipura", "Hunsur",
        "Krishnarajanagara", "Periyapatna", "Saragur", "Mandya", "Maddur", "Malavalli", "Srirangapatna",
        "Pandavapura", "Krishnarajpet", "Nagamangala", "Hassan", "Arsikere", "Channarayapatna", "Belur",
        "Sakleshpur", "Alur", "Madikeri", "Somwarpet", "Virajpet", "Shimoga", "Bhadravati", "Sagar", "Shikaripura",
        "Tirthahalli", "Soraba", "Hosanagara", "Tumkur", "Tiptur", "Gubbi", "Koratagere", "Sira", "Pavagada",
        "Madhugiri", "Kunigal", "Chiknayakanhalli", "Chamarajanagar", "Gundlupet", "Kollegal", "Yelandur",
        ],

    "telugu": [
        "Hyderabad", "Vijayawada", "Guntur", "Warangal", "Tirupati", "Nellore", "Visakhapatnam",
        "Kakinada", "Rajahmundry", "Kadapa", "Karimnagar", "Khammam", "Srikakulam", 
        "Vizianagaram", "Anantapur", "Chittoor", "Eluru", "Machilipatnam", 
        "Nizamabad", "Ongole", "Proddatur", "Adilabad", "Hanamkonda", 
        "Mahbubnagar", "Ramagundam", "Bhimavaram", "Hindupur", "Tenali", 
        "Chilakaluripet", "Markapur", "Amalapuram", "Madanapalle", 
        "Jagtial", "Tadepalligudem", "Mancherial", "Siddipet", "Miryalaguda", 
        "Bapatla", "Tuni", "Peddapuram", "Palacole", "Gudivada", 
        "Narasaraopet", "Vinukonda", "Kavali", "Nandigama", 
        "Gajuwaka", "Mangalagiri", "Dharmavaram", "Sattenapalle", "Zaheerabad",
    ],

    "english": [
    "Delhi", "New Delhi", "Lucknow", "Kanpur", "Ghaziabad", "Agra", "Meerut",
    "Allahabad", "Prayagraj", "Varanasi", "Noida", 
    "Jaipur", "Jodhpur", "Kota", "Udaipur", "Ajmer", "Bikaner",  # Rajasthan cities retained
    "Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala", 
    "Faridabad", "Gurugram", "Panipat", "Hisar", "Ambala", "Karnal", 
    "Patna", "Raipur", "Dehradun", "Haridwar", "Rishikesh", "Roorkee",
    "Haldwani", "Nainital", 
    "Shimla", "Manali", "Dharamshala", "Kullu", "Mandi", "Solan", 
    "Srinagar", "Jammu", "Anantnag", "Baramulla", "Udhampur", "Poonch",
    ],

    "tamil": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Puducherry", 
        "Erode", "Vellore", "Thoothukudi", "Dindigul", "Cuddalore", "Tiruppur", 
        "Thanjavur", "Kanchipuram", "Karur", "Nagercoil", "Tirunelveli", 
        "Kumbakonam", "Sivakasi", "Pudukkottai", "Pollachi", "Arakkonam", 
        "Nagapattinam", "Tiruvannamalai", "Udhagamandalam", "Namakkal", 
        "Tiruvallur", "Virudhunagar", "Dharmapuri", "Hosur", "Perambalur", 
        "Ariyalur", "Chengalpattu", "Ranipet", "Tenkasi", "Villupuram",
    ],
    
    "bengali": [
        "Kolkata", "Calcutta", "Kolikata", "City of Joy", "Kolkata City",
        "Kolkata Metropolitan", "Greater Kolkata", "Kolkata Nagar", "Calcutta City",
        "Kalikata", "Bengal's Capital", "Cultural Capital of India", "Kolkata Megacity",
        "Kolkata Urban", "Kolkata South", "Kolkata North", "Kolkata East", "Kolkata West",
        "Kolkata Central", "Kolkata Metro", "Kol", "KLT", "Kolkata Town", "Cal",
        "Kolkata District", "Kolkata Municipal", "Kolkata Borough", "Kolkata Heritage City",
        "Kolkata Port City", "Kolkata IT Hub", "Kolkata Financial Hub",
        "Asansol", "Siliguri", "Durgapur", "Bardhaman", "Darjeeling", 
        "Hooghly", "Howrah", "Kharagpur", "Haldia", "Malda", 
        "Raiganj", "Jalpaiguri", "Murshidabad", "Cooch Behar", 
        "Bankura", "Purulia", "Medinipur", "Balurghat", "Alipurduar", 
        "Suri", "Krishnanagar", "Tamluk", "Baharampur", "Chinsurah", 
        "Rampurhat", "Santipur", "Kandi", "Bongaon", "Basirhat", 
        "Habra", "Barrackpore", "Nabadwip", "Katwa", "Bolpur", "Uluberia",
    ],

    "english_pune": [
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar", "Bhavnagar", "Jamnagar", 
    "Bharuch", "Ankleshwar", "Valsad", "Navsari", "Bhuj", "Gandhidham", "Surendranagar", 
    "Junagadh", "Porbandar", "Patan", "Mehsana", "Dahod", "Godhra", "Modasa", "Morbi",
    "Veraval", "Palanpur", "Amreli", "Wankaner", "Anjar", "Nadiad", "Kheda", "Kapadwanj",
    "Himatnagar", "Unjha", "Limbdi", "Borsad", "Jetpur", "Dholka", "Sanasan", "Kalol",
    "Mahuva", "Viramgam", "Diu", "Daman", "Dahej", "Radhanpur", "Mansa", "Kadi",
    "Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain", "Rewa", "Satna", "Ratlam", 
    "Dewas", "Khargone", "Neemuch", "Shivpuri", "Chhindwara", "Sagar", "Sehore", 
    "Vidisha", "Shahdol", "Panna", "Katni", "Mandla", "Chhatarpur", "Tikamgarh", 
    "Narsinghpur", "Balaghat", "Burhanpur", "Betul", "Datia", "Maihar", "Mhow", 
    "Harda", "Pipariya", "Hoshangabad", "Ashoknagar", "Biaora", "Shajapur", "Rajgarh",
    "Kolaras", "Barela", "Dindori", "Sarni", "Pachmarhi", "Sohagpur", "Pachore", "Alirajpur",
    "Raisen", "Mauganj", "Kukshi", "Khandwa", "Pichhore", "Raghogarh", "Nagda", "Khurai",
    "Tapi", "Murwara", "Rampura", "Taloja", "Bhilai", "Chichli", "Mandvi", "Jasminabad", 
    "Badi", "Bamkheda", "Sanchi", "Sarafa", "Shujalpur", "Kutch", "Chhota Udepur", "Kudni"
],

    "english_dhanbad": [
    "Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Puri", "Sambalpur", "Balasore",
    "Koraput", "Kendrapara", 
    "Jharsuguda", "Jeypore", "Phulbani", "Angul", "Nayagarh", "Dhenkanal",
    "Gaya", "Bhagalpur", "Muzaffarpur", "Begusarai", "Munger", "Purnia", "Ara", "Chapra",
    "Darbhanga", "Nalanda", "Samastipur", "Saharsa", "Khagaria", "Siwan", "Buxar",
    "Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Bokaro Steel City", "Giridih", "Hazaribagh",
    "Deoghar", "Dumka", "Ramgarh", "Chaibasa", "Jamtara", "Simdega",
    "Guwahati", "Dibrugarh", "Jorhat", "Tinsukia", "Silchar", "Nagaon", "Tezpur", "Bongaigaon",
    "Sivasagar", "Barpeta", "Goalpara", "Nalbari",
    "Gangtok", "Namchi", "Mangan", "Rangpo", "Jorethang",
    "Itanagar", "Tawang", "Bomdila", "Ziro", "Pasighat", "Namsai", "Tezu", "Aalo", "Roing",
    "Kohima", "Dimapur", "Mokokchung", "Wokha", "Zunheboto", "Phek", "Mon", "Tuensang",
    "Imphal", "Thoubal", "Churachandpur", "Kangpokpi", "Bishnupur", "Jiribam",
    "Aizawl", "Lunglei", "Kolasib", "Champhai", "Serchhip", "Mamit", "Saiha",
    "Agartala", "Dharmanagar", "Udaipur", "Ambassa", "Kailashahar", "Teliamura", "Sonamura",
    "Shillong", "Tura", "Nongstoin", "Jowai", "Williamnagar",
    "Car Nicobar", "Great Nicobar", "Havelock", "Neil Island",
    ],
    
    "malayalam": [
    "Thiruvananthapuram", "Kochi", "Kozhikode", "Kannur", "Kottayam", 
    "Alappuzha", "Palakkad", "Thrissur", "Malappuram", "Muvattupuzha", 
    "Vypin", "Varkala", "Adoor", "Pathanamthitta", "Irinjalakuda", 
    "Ernakulam", "Punalur", "Kasaragod", "Payyanur", "Neyyattinkara", 
    "Kalpetta", "Perumbavoor", "Thalassery", "Manjeri", "Kasargod", 
    "Kollam", "Anchal", "Aluva", "Muvattupuzha", "Kanhangad", 
    "Pattambi", "Perinthalmanna", "Sreekariyam", "Azhikkal", "Chalakudy",
    ],
    
    
    
}


file_langs = {
    "marathi": [{"email": "recruitment.west@evisiontechnoserve.com", "password": "fzdd bglt ctgc qutw"},"new_email_message_west.html"], # Monali Mam Pune
    "kannada": [{"email": "recruitment.south@evisiontechnoserve.com", "password": "zjnn gnnb yyix gqgg"},"new_email_message_south.html"], # Deepti Mam Bangalore
    "telugu": [{"email": "recruitment.south@evisiontechnoserve.com", "password": "zjnn gnnb yyix gqgg"},"new_email_message_south.html"], # Deepti Mam Bangalore
    "english": [{"email": "recruitment.north@evisiontechnoserve.com", "password": "bnrf ruqo dcqy ajql"},"new_email_message_north.html"], # Anamika Mam Delhi
    "english_pune": [{"email": "recruitment.west@evisiontechnoserve.com", "password": "fzdd bglt ctgc qutw"},"new_email_message_west.html"], # Monali Mam Pune
    "english_dhanbad": [{"email": "recruitment.east@evisiontechnoserve.com", "password": "vkgr gbqq ynib xkjx"},"new_email_message_east.html"], # Sati Mam Dhanbad
    "tamil": [{"email": "recruitment.south@evisiontechnoserve.com", "password": "zjnn gnnb yyix gqgg"},"new_email_message_south.html"], # Deepti Mam Bangalore
    "bengali": [{"email": "recruitment.east@evisiontechnoserve.com", "password": "vkgr gbqq ynib xkjx"},"new_email_message_east.html"], # Sati Mam Dhanbad  
    "malayalam": [{"email": "recruitment.south@evisiontechnoserve.com", "password": "zjnn gnnb yyix gqgg"},"new_email_message_south.html"], # Deepti Mam Bangalore
        
    
    }


def check_city(input_city,lang):
    for city in city_by_langs[lang]:
        if is_same(input_city,city):
            return True
    return False
    


def city_to_lang(input_city):
    for lang in city_by_langs:
        if check_city(input_city,lang):
            return file_langs[lang]
    return file_langs['english']





#--------------------Load and Dump json data---------------------

def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        x = json.load(f)
    return x

def dump_json(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


#-------------------Read and write File-------------------------
        
def readit(file_path):
    with open(file_path,'r',encoding='utf-8') as file:
        content =file.read()
    return content

def writeit(file_path,content):
    with open(file_path,'w',encoding='utf-8') as file:
        file.write(content)
    
        




#----------------------------Sound Operations------------------------------------

from gtts import gTTS
import os

def speak(text, lang='en', filename='output.mp3',speed=1.09):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    os.system(f'play {filename} tempo {speed}')
    os.remove(filename)


def check_internet(text):
    while True:
        try:
            speak(text)
            break
        except:
            time.sleep(1)
    return None


def isinternet():
    try:
        speak('Internet is On')
        return True
    except:
        return False
    

#--------------------------------------Check Battery------------------------------------

import psutil

def check_battery(threshold=20):
    battery = psutil.sensors_battery()
    if battery is None:
        print("Battery status not available.")
        return

    percent = battery.percent
    if percent < threshold and not battery.power_plugged:
        print(f"⚠️ Warning: Low Battery - {percent}% remaining. Please plug in your charger.")
        return False
    else:
        print(f"Battery level: {percent}%. Status is OK.")
        return True








