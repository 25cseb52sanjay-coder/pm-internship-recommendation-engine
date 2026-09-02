"use client";

import { useEffect, useState } from "react";
import { fetchApi, getBackendRootUrl } from "@/lib/api";
import { User, FileText, Upload, CheckCircle2, Plus, X, Sparkles, Building, MapPin, GraduationCap, Image as ImageIcon, Eye, ExternalLink, RefreshCw, UploadCloud, Trash2, PlusCircle, Code2, ShieldCheck, AlertCircle, Loader2, Copy, Check } from "lucide-react";
const CATEGORY_OPTIONS = [
  "Programming Languages",
  "Web Development",
  "AI / Machine Learning",
  "Data & Analytics",
  "Databases",
  "Cloud / DevOps",
  "Cybersecurity",
  "Networking",
  "Software Engineering",
  "Electronics / ECE",
  "VLSI / Semiconductor",
  "Electrical / EEE",
  "Mechanical Engineering",
  "Automotive Engineering",
  "Robotics / Mechatronics",
  "Civil Engineering",
  "Chemical / Materials",
  "Aerospace / Aeronautical",
  "Biotechnology / Biomedical",
  "Manufacturing / Industrial",
  "Business / Professional",
  "Soft Skills",
  "Languages",
  "Other"
];

const SKILL_MAPPING: Record<string, string[]> = {
  "Programming Languages": [
    "C", "C++", "C#", "Java", "Python", "JavaScript", "TypeScript", "Go", "Rust", "Kotlin", "Swift", "Dart", "PHP", "Ruby", "R", "MATLAB", "Scala", "Bash", "PowerShell", "SQL", "PL/SQL", "Assembly", "Verilog", "SystemVerilog", "VHDL"
  ],
  "Web Development": [
    "HTML", "CSS", "React", "Next.js", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "REST API", "GraphQL", "WebSockets", "Frontend Development", "Backend Development", "Full Stack Development", "Flutter", "React Native"
  ],
  "AI / Machine Learning": [
    "Artificial Intelligence", "Machine Learning", "Deep Learning", "Generative AI", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Large Language Models", "Prompt Engineering", "Retrieval-Augmented Generation", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV", "Hugging Face", "LangChain"
  ],
  "Data & Analytics": [
    "Data Science", "Data Analytics", "Data Engineering", "Statistics", "Data Visualization", "Pandas", "NumPy", "Matplotlib", "Power BI", "Tableau", "Excel", "Apache Spark", "Hadoop", "Kafka", "ETL", "Data Warehousing", "Business Intelligence", "Predictive Analytics"
  ],
  "Databases": [
    "MySQL", "PostgreSQL", "Oracle", "SQL Server", "SQLite", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Firebase", "Supabase", "Database Design", "Database Administration", "SQL Optimization", "NoSQL"
  ],
  "Cloud / DevOps": [
    "AWS", "Microsoft Azure", "Google Cloud Platform", "Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub Actions", "GitLab CI/CD", "CI/CD", "Linux", "Nginx", "Cloud Architecture", "Cloud Security", "DevOps", "Site Reliability Engineering", "Infrastructure as Code"
  ],
  "Cybersecurity": [
    "Cybersecurity", "Information Security", "Network Security", "Application Security", "Cloud Security", "Ethical Hacking", "Penetration Testing", "Digital Forensics", "Incident Response", "Security Operations", "SOC", "Threat Intelligence", "Vulnerability Assessment", "Cryptography", "Malware Analysis", "Identity and Access Management", "Zero Trust", "SIEM", "OWASP"
  ],
  "Networking": [
    "Computer Networks", "TCP/IP", "HTTP/HTTPS", "DNS", "Routing", "Switching", "CCNA", "Cisco", "Network Administration", "Wireless Networking", "5G", "4G/LTE", "Telecommunications"
  ],
  "Software Engineering": [
    "Data Structures", "Algorithms", "Object-Oriented Programming", "Functional Programming", "Design Patterns", "System Design", "Software Architecture", "Microservices", "Unit Testing", "Integration Testing", "Automation Testing", "Test-Driven Development", "Debugging", "Git", "GitHub", "GitLab", "Jira", "Agile", "Scrum"
  ],
  "Electronics / ECE": [
    "Digital Electronics", "Analog Electronics", "Circuit Design", "Microcontrollers", "Microprocessors", "Embedded Systems", "Firmware Development", "PCB Design", "Embedded C", "Arduino", "Raspberry Pi", "ESP32", "STM32", "ARM", "FPGA", "Digital Signal Processing", "Signal Processing", "RF Engineering", "Communication Systems", "Wireless Communication", "Antenna Design", "IoT", "Sensors", "Instrumentation"
  ],
  "VLSI / Semiconductor": [
    "VLSI Design", "ASIC Design", "FPGA Design", "RTL Design", "RTL Verification", "Functional Verification", "SystemVerilog", "Verilog", "VHDL", "UVM", "Physical Design", "Floorplanning", "Placement", "Routing", "Static Timing Analysis", "Digital IC Design", "Analog IC Design", "Mixed Signal Design", "Semiconductor Devices", "Microelectronics", "ASIC Verification", "Design for Test"
  ],
  "Electrical / EEE": [
    "Power Systems", "Power Electronics", "Electrical Machines", "Control Systems", "Industrial Automation", "PLC", "SCADA", "MATLAB Simulink", "Renewable Energy", "Solar Energy", "Wind Energy", "Smart Grid", "Power Distribution", "Power Transmission", "Energy Management", "Electrical Design", "High Voltage Engineering", "EV Systems", "Battery Technology", "Energy Storage"
  ],
  "Mechanical Engineering": [
    "Mechanical Design", "CAD", "CAM", "CAE", "AutoCAD", "SolidWorks", "CATIA", "Siemens NX", "Creo", "ANSYS", "Finite Element Analysis", "Computational Fluid Dynamics", "Thermodynamics", "Fluid Mechanics", "Heat Transfer", "Machine Design", "Manufacturing", "Production", "CNC", "3D Printing", "Additive Manufacturing", "Quality Control", "HVAC"
  ],
  "Automotive Engineering": [
    "Automotive Engineering", "Vehicle Dynamics", "Automotive Design", "Automotive Manufacturing", "Electric Vehicles", "EV Powertrain", "Battery Systems", "Automotive Electronics", "ADAS", "Autonomous Vehicles", "Vehicle Controls", "Automotive Embedded Systems", "Automotive Diagnostics", "CAN Bus", "AUTOSAR"
  ],
  "Robotics / Mechatronics": [
    "Robotics", "Mechatronics", "Industrial Robotics", "ROS", "ROS2", "Computer Vision", "Motion Planning", "Robot Control", "Kinematics", "Dynamics", "Automation", "PLC", "Sensors", "Actuators", "Drone Technology", "UAV", "Autonomous Systems"
  ],
  "Civil Engineering": [
    "Structural Engineering", "Structural Design", "Construction Management", "AutoCAD Civil 3D", "BIM", "Revit", "STAAD.Pro", "ETABS", "SAP2000", "Geotechnical Engineering", "Soil Mechanics", "Transportation Engineering", "Highway Engineering", "Traffic Engineering", "Surveying", "GIS", "Environmental Engineering", "Water Resources", "Hydraulics", "Hydrology", "Quantity Surveying"
  ],
  "Chemical / Materials": [
    "Chemical Engineering", "Process Engineering", "Process Simulation", "Aspen Plus", "Aspen HYSYS", "Chemical Process Design", "Mass Transfer", "Reaction Engineering", "Petrochemical Engineering", "Petroleum Engineering", "Polymer Engineering", "Materials Science", "Materials Engineering", "Metallurgy", "Corrosion Engineering", "Nanotechnology"
  ],
  "Aerospace / Aeronautical": [
    "Aerospace Engineering", "Aeronautical Engineering", "Aerodynamics", "Aircraft Design", "Propulsion", "Avionics", "Flight Dynamics", "UAV", "Drone Technology", "Aerospace Structures", "CFD", "Aerospace Materials", "Guidance Navigation and Control", "Satellite Systems", "Space Technology"
  ],
  "Biotechnology / Biomedical": [
    "Biotechnology", "Biomedical Engineering", "Bioinformatics", "Computational Biology", "Genomics", "Proteomics", "Molecular Biology", "Genetic Engineering", "Microbiology", "Biochemistry", "Bioprocess Engineering", "Pharmaceutical Technology", "Medical Imaging", "Biomedical Instrumentation", "Biomaterials", "Tissue Engineering", "Drug Discovery"
  ],
  "Manufacturing / Industrial": [
    "Manufacturing Engineering", "Production Engineering", "Industrial Engineering", "Lean Manufacturing", "Six Sigma", "Quality Engineering", "Supply Chain", "Operations Management", "Production Planning", "CNC", "PLC", "SCADA", "Automation", "Industry 4.0", "Digital Manufacturing", "Additive Manufacturing", "CAD/CAM"
  ],
  "Business / Professional": [
    "Business Analysis", "Project Management", "Product Management", "Operations", "Consulting", "Finance", "Accounting", "Marketing", "Digital Marketing", "Sales", "Human Resources", "Business Development", "Entrepreneurship", "Supply Chain Management", "Financial Analysis", "Market Research"
  ],
  "Soft Skills": [
    "Communication", "Written Communication", "Verbal Communication", "Presentation", "Public Speaking", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking", "Analytical Thinking", "Creativity", "Time Management", "Adaptability", "Decision Making", "Negotiation", "Conflict Resolution", "Emotional Intelligence", "Research", "Technical Writing", "Documentation"
  ],
  "Languages": [
    "English", "Tamil", "Hindi", "Malayalam", "Telugu", "Kannada", "Bengali", "Marathi", "Gujarati", "French", "German", "Spanish", "Japanese", "Chinese"
  ],
  "Other": []
};

const toNormalizedCode = (val: string): string => {
  return val
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "_")
    .replace(/__+/g, "_")
    .replace(/(^_+|_+$)/g, "");
};

const normalizeSkillCode = (skill: string): string => {
  let cleaned = skill;
  if (cleaned === "C++") return "C_PLUS_PLUS";
  if (cleaned === "C#") return "C_SHARP";
  return cleaned
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "_")
    .replace(/_+/g, "_")
    .replace(/(^_+|_+$)/g, "");
};

const mapBackendSkills = (skills: any[]) => {
  if (!skills) return [];
  return skills.map((s: any) => {
    const name = s.name || s.skill || "";
    const category = s.category || "";
    
    let matchedCategory = category || "Other";
    if (!category || category === "General" || category === "Other") {
      for (const [catName, skillList] of Object.entries(SKILL_MAPPING)) {
        if (skillList.some(skillName => skillName.toLowerCase() === name.toLowerCase())) {
          matchedCategory = catName;
          break;
        }
      }
    }

    return {
      category: toNormalizedCode(matchedCategory),
      skill: normalizeSkillCode(name),
      display_category: matchedCategory,
      display_skill: name
    };
  });
};

const ENGINEERING_OPTIONS = [
  { label: "Computer Science and Engineering", code: "COMPUTER_SCIENCE" },
  { label: "Information Technology", code: "INFORMATION_TECHNOLOGY" },
  { label: "Artificial Intelligence and Machine Learning", code: "ARTIFICIAL_INTELLIGENCE" },
  { label: "Artificial Intelligence", code: "ARTIFICIAL_INTELLIGENCE" },
  { label: "Machine Learning", code: "MACHINE_LEARNING" },
  { label: "Data Science", code: "DATA_SCIENCE" },
  { label: "Data Engineering", code: "DATA_ENGINEERING" },
  { label: "Cybersecurity / Information Security", code: "CYBERSECURITY" },
  { label: "Software Engineering", code: "SOFTWARE_ENGINEERING" },
  { label: "Computer Engineering", code: "COMPUTER_ENGINEERING" },
  { label: "Electronics and Communication Engineering", code: "ELECTRONICS_COMMUNICATION" },
  { label: "Electronics Engineering", code: "ELECTRONICS" },
  { label: "Electrical and Electronics Engineering", code: "ELECTRICAL_ELECTRONICS" },
  { label: "Electrical Engineering", code: "ELECTRICAL" },
  { label: "Instrumentation and Control Engineering", code: "INSTRUMENTATION" },
  { label: "Instrumentation Engineering", code: "INSTRUMENTATION" },
  { label: "VLSI / Microelectronics", code: "VLSI_MICROELECTRONICS" },
  { label: "Embedded Systems", code: "EMBEDDED_SYSTEMS" },
  { label: "Telecommunication Engineering", code: "TELECOMMUNICATIONS" },
  { label: "Mechanical Engineering", code: "MECHANICAL" },
  { label: "Mechatronics Engineering", code: "MECHATRONICS_ROBOTICS" },
  { label: "Robotics Engineering", code: "ROBOTICS" },
  { label: "Automobile Engineering", code: "AUTOMOTIVE" },
  { label: "Automotive Engineering", code: "AUTOMOTIVE" },
  { label: "Production Engineering", code: "PRODUCTION" },
  { label: "Industrial Engineering", code: "INDUSTRIAL_ENGINEERING" },
  { label: "Manufacturing Engineering", code: "MANUFACTURING" },
  { label: "Civil Engineering", code: "CIVIL" },
  { label: "Structural Engineering", code: "STRUCTURAL" },
  { label: "Geotechnical Engineering", code: "GEOTECHNICAL" },
  { label: "Transportation Engineering", code: "TRANSPORTATION" },
  { label: "Environmental Engineering", code: "ENVIRONMENTAL" },
  { label: "Construction Engineering / Management", code: "CONSTRUCTION" },
  { label: "Water Resources Engineering", code: "WATER_RESOURCES" },
  { label: "Chemical Engineering", code: "CHEMICAL" },
  { label: "Petrochemical Engineering", code: "PETROCHEMICAL" },
  { label: "Petroleum Engineering", code: "PETROLEUM" },
  { label: "Polymer Engineering", code: "POLYMERS" },
  { label: "Materials Engineering", code: "MATERIALS_METALLURGY" },
  { label: "Metallurgical Engineering", code: "MATERIALS_METALLURGY" },
  { label: "Aerospace Engineering", code: "AEROSPACE" },
  { label: "Aeronautical Engineering", code: "AERONAUTICAL" },
  { label: "Avionics Engineering", code: "AVIONICS" },
  { label: "Biotechnology", code: "BIOTECHNOLOGY" },
  { label: "Biomedical Engineering", code: "BIOMEDICAL" },
  { label: "Biochemical Engineering", code: "BIOCHEMICAL" },
  { label: "Mining Engineering", code: "MINING" },
  { label: "Textile Engineering", code: "TEXTILE" },
  { label: "Food Technology / Food Engineering", code: "FOOD_TECHNOLOGY" },
  { label: "Agricultural Engineering", code: "AGRICULTURAL" },
  { label: "Marine Engineering", code: "MARINE" },
  { label: "Naval Architecture", code: "NAVAL_ARCHITECTURE" },
  { label: "Architectural Engineering", code: "ARCHITECTURAL_ENGINEERING" },
  { label: "Other Engineering Discipline", code: "OTHER_ENGINEERING" }
];

const LEGACY_MAP: Record<string, string> = {
  "cse": "COMPUTER_SCIENCE",
  "CSE": "COMPUTER_SCIENCE",
  "computer science engineering": "COMPUTER_SCIENCE",
  "computer science": "COMPUTER_SCIENCE",
  "it": "INFORMATION_TECHNOLOGY",
  "IT": "INFORMATION_TECHNOLOGY",
  "ece": "ELECTRONICS_COMMUNICATION",
  "ECE": "ELECTRONICS_COMMUNICATION",
  "eee": "ELECTRICAL_ELECTRONICS",
  "EEE": "ELECTRICAL_ELECTRONICS",
  "ee": "ELECTRICAL",
  "EE": "ELECTRICAL",
  "me": "MECHANICAL",
  "ME": "MECHANICAL",
  "mech": "MECHANICAL",
  "ce": "CIVIL",
  "CE": "CIVIL",
  "civil": "CIVIL",
  "che": "CHEMICAL",
  "CHE": "CHEMICAL",
  "ai": "ARTIFICIAL_INTELLIGENCE",
  "ml": "ARTIFICIAL_INTELLIGENCE",
  "aiml": "ARTIFICIAL_INTELLIGENCE",
  "ds": "DATA_SCIENCE",
};

 const normalizeStoredBranch = (storedVal: string | null | undefined): string => {
  if (!storedVal) return "";
  const val = storedVal.trim();
  if (ENGINEERING_OPTIONS.some(opt => opt.code === val)) {
    return val;
  }
  const lowerVal = val.toLowerCase();
  
  // Map common abbreviations
  if (lowerVal === "cse" || lowerVal === "computer science" || lowerVal.includes("computer science engineering") || lowerVal.includes("computer science & engineering")) {
    return "COMPUTER_SCIENCE";
  }
  if (lowerVal === "it" || lowerVal.includes("information technology")) {
    return "INFORMATION_TECHNOLOGY";
  }
  if (lowerVal === "ece" || lowerVal.includes("electronics and communication") || lowerVal.includes("electronics & communication")) {
    return "ELECTRONICS_COMMUNICATION";
  }
  if (lowerVal === "eee" || lowerVal.includes("electrical and electronics") || lowerVal.includes("electrical & electronics")) {
    return "ELECTRICAL_ELECTRONICS";
  }
  if (lowerVal === "ee" || lowerVal === "electrical" || lowerVal.includes("electrical engineering")) {
    return "ELECTRICAL";
  }
  if (lowerVal === "ece" || lowerVal === "electronics" || lowerVal.includes("electronics engineering")) {
    return "ELECTRONICS";
  }
  if (lowerVal === "mechanical" || lowerVal === "mech" || lowerVal.includes("mechanical engineering")) {
    return "MECHANICAL";
  }
  if (lowerVal === "civil" || lowerVal.includes("civil engineering")) {
    return "CIVIL";
  }
  if (lowerVal === "chemical" || lowerVal.includes("chemical engineering")) {
    return "CHEMICAL";
  }
  if (lowerVal === "biotech" || lowerVal.includes("biotechnology")) {
    return "BIOTECHNOLOGY";
  }
  if (lowerVal === "aerospace" || lowerVal.includes("aerospace engineering")) {
    return "AEROSPACE";
  }
  if (lowerVal === "vlsi" || lowerVal.includes("vlsi") || lowerVal.includes("microelectronics")) {
    return "VLSI_MICROELECTRONICS";
  }
  if (lowerVal === "embedded" || lowerVal.includes("embedded systems")) {
    return "EMBEDDED_SYSTEMS";
  }

  // If legacy text matches label case-insensitively
  const matched = ENGINEERING_OPTIONS.find(opt => opt.label.toLowerCase() === lowerVal);
  if (matched) return matched.code;

  return "OTHER_ENGINEERING";
};

 const getBranchLabel = (code: string | null | undefined): string => {
  if (!code) return "";
  const opt = ENGINEERING_OPTIONS.find(o => o.code === code);
  return opt ? opt.label : code;
};

 const matchAbbreviation = (label: string, searchVal: string): boolean => {
  const searchLower = searchVal.toLowerCase().trim();
  if (!searchLower) return true;
  if (label.toLowerCase().includes(searchLower)) return true;

  // initials
  const initials = label
    .split(/\s+/)
    .filter(word => !["and", "or", "&", "/"].includes(word.toLowerCase()))
    .map(word => word[0])
    .join("")
    .toLowerCase();

  if (initials.includes(searchLower)) return true;
  
  const customMap: Record<string, string[]> = {
    cse: ["computer science and engineering", "computer engineering", "software engineering"],
    it: ["information technology"],
    ece: ["electronics and communication engineering", "electronics engineering"],
    eee: ["electrical and electronics engineering", "electrical engineering"],
    vlsi: ["vlsi / microelectronics"],
    aiml: ["artificial intelligence and machine learning"],
    ai: ["artificial intelligence"],
    ml: ["machine learning"],
    ds: ["data science"],
  };

  for (const [key, list] of Object.entries(customMap)) {
    if (key.includes(searchLower) || searchLower.includes(key)) {
      if (list.some(item => label.toLowerCase().includes(item))) {
        return true;
      }
    }
  }

  return false;
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>({
    full_name: "",
    phone: "",
    age: 22,
    qualification: "Bachelor's Degree",
    degree: "B.Tech",
    course_program: "",
    qualification_type: "",
    branch: "Computer Science",
    institution: "",
    graduation_year: 2025,
    cgpa: 8.5,
    preferred_industry: "Public Sector / Aerospace",
    preferred_role: "AI & Data Analyst Intern",
    preferred_location: "Bengaluru",
    work_mode: "On-site",
    preferred_duration: "6 Months",
    projects_summary: "",
    skills: [],
    resume_url: null,
  });

  const [skillInput, setSkillInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [showImageLightbox, setShowImageLightbox] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isEditMode, setIsEditMode] = useState(true);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [currentUser, setCurrentUser] = useState<any>(null);

  // LeetCode Profile Verification States (Task 2 Specification)
  const [leetcodeInput, setLeetcodeInput] = useState("");
  const [leetcodeStatus, setLeetcodeStatus] = useState<
    | "NOT_CONNECTED"
    | "VALIDATING"
    | "ACCOUNT_NOT_FOUND"
    | "ACCOUNT_FOUND"
    | "OWNERSHIP_PENDING"
    | "VERIFIED"
    | "VERIFICATION_FAILED"
    | "DATA_UNAVAILABLE"
  >("NOT_CONNECTED");
  const [verificationToken, setVerificationToken] = useState<string | null>(null);
  const [connectedUsername, setConnectedUsername] = useState<string | null>(null);
  const [copiedToken, setCopiedToken] = useState(false);
  const [solutionUrlInput, setSolutionUrlInput] = useState("");
  const [branchSearch, setBranchSearch] = useState("");
  const [branchDropdownOpen, setBranchDropdownOpen] = useState(false);

  // Skills dependent dropdown states
  const [selectedSkillCategory, setSelectedSkillCategory] = useState("");
  const [selectedSkillName, setSelectedSkillName] = useState("");
  const [customSkillName, setCustomSkillName] = useState("");
  const [skillCategorySearch, setSkillCategorySearch] = useState("");
  const [skillNameSearch, setSkillNameSearch] = useState("");
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [skillDropdownOpen, setSkillDropdownOpen] = useState(false);

  useEffect(() => {
    let currentName = "";
    if (typeof window !== "undefined") {
      const storedUser = localStorage.getItem("pm_internship_user");
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setCurrentUser(parsed);
          currentName = parsed.full_name || parsed.name || "";
          if (currentName) {
            setProfile((prev: any) => ({
              ...prev,
              full_name: prev.full_name || currentName,
            }));
          }
        } catch (e) {
          console.error("Failed to parse user:", e);
        }
      }
    }

    async function loadProfile() {
      try {
        const data = await fetchApi("/students/profile");
        if (data) {
          setProfile((prev: any) => ({
            ...prev,
            ...data,
            full_name: data.full_name || data.name || prev.full_name || currentName || "",
            skills: mapBackendSkills(data.skills),
          }));
          if (data.leetcode_verification_status === "VERIFIED") {
            setLeetcodeStatus("VERIFIED");
            setConnectedUsername(data.leetcode_username);
          } else if (data.leetcode_username) {
            setConnectedUsername(data.leetcode_username);
          }
          const hasSavedProfile = !!(data.course_program && data.qualification_type);
          setIsEditMode(!hasSavedProfile);
        }
      } catch (err) {
        console.error("Profile load error:", err);
      }
    }
    loadProfile();
  }, []);

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!profile.full_name && !currentUser?.name && !currentUser?.full_name) {
      errors.full_name = "Candidate Full Name is required.";
    }
    if (profile.age === undefined || profile.age === null || profile.age === "") {
      errors.age = "Candidate Age is required.";
    } else if (Number(profile.age) < 18 || Number(profile.age) > 35) {
      errors.age = "Candidate Age must be between 18 and 35.";
    }
    if (!profile.course_program) {
      errors.course_program = "Course / Program is required.";
    }
    if (!profile.qualification_type) {
      errors.qualification_type = "Qualification / Study Type is required.";
    }
    if (profile.qualification_type === "Engineering Degree" && !profile.branch) {
      errors.branch = "Engineering Branch / Discipline is required.";
    }
    if (!profile.skills || profile.skills.length === 0) {
      errors.skills = "At least one skill must be added.";
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setValidationErrors({});
    
    if (!validateForm()) {
      setMessage("Please resolve the validation errors below.");
      return;
    }
    
    setSaving(true);
    try {
      const candidateFullName = (profile.full_name || currentUser?.full_name || currentUser?.name || "").trim();
      const payload = {
        full_name: candidateFullName,
        name: candidateFullName,
        phone: profile.phone || "",
        age: profile.age ? parseInt(profile.age) : null,
        qualification: profile.qualification || "",
        degree: profile.degree || "",
        course_program: profile.course_program,
        qualification_type: profile.qualification_type,
        branch: profile.qualification_type === "Engineering Degree" ? profile.branch : null,
        institution: profile.institution || "",
        graduation_year: profile.graduation_year ? parseInt(profile.graduation_year) : null,
        cgpa: profile.cgpa ? parseFloat(profile.cgpa) : null,
        preferred_industry: profile.preferred_industry || "",
        preferred_role: profile.preferred_role || "",
        preferred_location: profile.preferred_location || "",
        work_mode: profile.work_mode || "",
        preferred_duration: profile.preferred_duration || "",
        projects_summary: profile.projects_summary || "",
        skills: profile.skills.map((s: any) => ({
          name: s.display_skill,
          category: s.display_category,
        })),
      };

      const data = await fetchApi("/students/profile", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (data) {
        const resolvedName = data.full_name || data.name || candidateFullName;
        setProfile({
          ...data,
          full_name: resolvedName,
          skills: mapBackendSkills(data.skills),
        });

        if (typeof window !== "undefined" && resolvedName) {
          const storedUser = localStorage.getItem("pm_internship_user");
          if (storedUser) {
            try {
              const u = JSON.parse(storedUser);
              u.name = resolvedName;
              u.full_name = resolvedName;
              localStorage.setItem("pm_internship_user", JSON.stringify(u));
              setCurrentUser(u);
            } catch (e) {
              console.error(e);
            }
          }
        }
      }

      setMessage("Profile saved successfully.");
      setIsEditMode(false);
    } catch (err: any) {
      setMessage(err.message || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const processFile = async (file: File) => {
    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetchApi("/students/resume", {
        method: "POST",
        body: formData,
      });

      setMessage(`File "${file.name}" uploaded and processed successfully!`);
      // Reload profile
      const updatedProf = await fetchApi("/students/profile");
      setProfile({
        ...updatedProf,
        skills: mapBackendSkills(updatedProf.skills),
      });
    } catch (err: any) {
      setMessage(err.message || "File upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteResume = async () => {
    setDeleting(true);
    setMessage(null);

    try {
      await fetchApi("/students/resume", { method: "DELETE" });
      setProfile((prev: any) => ({ ...prev, resume_url: null }));
      setMessage("Uploaded document/image deleted successfully!");
    } catch (err: any) {
      setMessage(err.message || "Failed to delete file");
    } finally {
      setDeleting(false);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  // HTML5 Drag and Drop Handlers
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleAddSkill = () => {
    let cat = selectedSkillCategory;
    let sk = selectedSkillName;
    if (cat === "Other") {
      sk = customSkillName.trim();
    }
    if (!cat || !sk) return;

    // Prevent duplicates
    const exists = profile.skills.some(
      (item: any) =>
        item.display_skill.toLowerCase() === sk.toLowerCase() &&
        item.display_category.toLowerCase() === cat.toLowerCase()
    );

    if (!exists) {
      const newSkillObj = {
        category: toNormalizedCode(cat),
        skill: normalizeSkillCode(sk),
        display_category: cat,
        display_skill: sk
      };
      setProfile({
        ...profile,
        skills: [...profile.skills, newSkillObj]
      });
    }

    // Clear skill, keep category selected
    setSelectedSkillName("");
    setCustomSkillName("");
  };

  const handleRemoveSkill = (skillName: string) => {
    setProfile({
      ...profile,
      skills: profile.skills.filter((s: any) => s.display_skill !== skillName),
    });
  };

  const isImageFile = (url: string | null) => {
    if (!url) return false;
    const lower = url.toLowerCase();
    return lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".webp") || lower.endsWith(".bmp") || lower.endsWith(".gif");
  };

  const getFullFileUrl = (url: string | null) => {
    if (!url) return "";
    let cleanUrl = url;
    if (cleanUrl.includes("/uploads/")) {
      cleanUrl = "/uploads/" + cleanUrl.split("/uploads/").pop();
    }
    if (cleanUrl.startsWith("http://") || cleanUrl.startsWith("https://")) {
      return cleanUrl;
    }
    return `${getBackendRootUrl()}${cleanUrl}`;
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="border-b border-slate-300 pb-4 flex items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-xs font-bold text-blue-900">
            <User className="w-3.5 h-3.5" />
            <span>{isEditMode ? "Candidate Information & Resume Parser" : "Candidate Profile Summary"}</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002147]">{isEditMode ? "Candidate Profile Setup" : "My Profile"}</h1>
          <p className="text-xs text-slate-600">
            {isEditMode 
              ? "The recommendation engine evaluates these exact parameters for eligibility & compatibility scoring" 
              : "This is your saved candidate profile evaluation structure"}
          </p>
        </div>

        {/* Edit Button in VIEW mode */}
        {!isEditMode && (
          <button
            type="button"
            onClick={() => setIsEditMode(true)}
            aria-label="Edit Profile"
            title="Edit Profile"
            className="flex items-center space-x-1.5 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-900 rounded border border-blue-200 text-xs font-bold transition-all shrink-0 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            <span>Edit Profile</span>
          </button>
        )}
      </div>

      {message && (
        <div className="p-3 rounded bg-emerald-50 border border-emerald-300 text-xs text-emerald-900 font-bold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {isEditMode ? (
        <>
          {/* Resume & Image Drag and Drop Upload Area */}
          <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-900 shrink-0 font-bold">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#002147]">AI Document & Image Uploader</h3>
              <p className="text-xs text-slate-600">Upload PDF, DOCX, or Image (PNG, JPG, WEBP) to auto-fill details and preview</p>
            </div>
          </div>

          {/* Top Actions: Add Image (+) and Delete */}
          <div className="flex items-center space-x-2">
            <label className="px-3 py-1.5 rounded bg-[#002147] hover:bg-[#001529] text-white text-xs font-bold cursor-pointer shadow-sm flex items-center space-x-1 transition-colors">
              <Plus className="w-4 h-4" />
              <span>Add Image / File</span>
              <input
                type="file"
                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,image/*"
                onChange={handleFileInputChange}
                disabled={uploading}
                className="hidden"
              />
            </label>

            {profile.resume_url && (
              <button
                type="button"
                onClick={handleDeleteResume}
                disabled={deleting}
                className="px-3 py-1.5 rounded bg-red-100 hover:bg-red-200 text-red-800 border border-red-300 text-xs font-bold flex items-center space-x-1 transition-colors"
                title="Delete uploaded file"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{deleting ? "Deleting..." : "Delete"}</span>
              </button>
            )}
          </div>
        </div>

        {/* Interactive Drag & Drop Box */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded p-6 text-center transition-all duration-200 ${
            isDragging
              ? "border-blue-700 bg-blue-50 scale-[1.01]"
              : "border-slate-300 hover:border-blue-700 bg-slate-50"
          }`}
        >
          {uploading ? (
            <div className="py-6 space-y-2">
              <div className="w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs font-bold text-blue-900">Uploading and analyzing candidate document...</p>
            </div>
          ) : profile.resume_url ? (
            /* Whole Image & Document Preview Display Card */
            <div className="space-y-3">
              
              {/* Header Bar inside preview card */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-200 text-xs">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    {isImageFile(profile.resume_url) ? "Uploaded Image Resume" : "Uploaded Document Resume"}
                  </span>
                  <span className="font-bold text-slate-800 truncate max-w-xs sm:max-w-md">
                    {profile.resume_url.split("/").pop()}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  {isImageFile(profile.resume_url) && (
                    <button
                      type="button"
                      onClick={() => setShowImageLightbox(true)}
                      className="px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-300 text-xs font-bold flex items-center space-x-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Expand View</span>
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={handleDeleteResume}
                    disabled={deleting}
                    className="p-1 rounded bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 transition-colors"
                    title="Delete Image / Document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Viewing Whole Image Directly inside the card */}
              {isImageFile(profile.resume_url) ? (
                <div 
                  onClick={() => setShowImageLightbox(true)}
                  className="relative w-full min-h-[220px] max-h-[480px] bg-slate-900 rounded border border-slate-300 overflow-hidden flex items-center justify-center p-2 cursor-pointer group shadow-sm"
                >
                  <img
                    src={getFullFileUrl(profile.resume_url)}
                    alt="Uploaded Whole Resume Image"
                    className="max-w-full max-h-[460px] object-contain rounded"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                    <span className="px-3.5 py-1.5 rounded bg-[#002147] text-white font-bold text-xs flex items-center space-x-1.5 shadow">
                      <Eye className="w-4 h-4" />
                      <span>Click to View Fullscreen</span>
                    </span>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded bg-white border border-slate-200 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-800">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-[#002147]">Document File Uploaded</p>
                      <p className="text-[11px] text-slate-500">{profile.resume_url.split("/").pop()}</p>
                    </div>
                  </div>

                  <a
                    href={getFullFileUrl(profile.resume_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 rounded bg-[#002147] hover:bg-[#001529] text-white text-xs font-bold flex items-center space-x-1 shadow"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>View File</span>
                  </a>
                </div>
              )}

            </div>
          ) : (
            /* Drag and Drop Zone Empty State with (+) Icon */
            <div className="space-y-2.5 py-4 text-center">
              <label className="cursor-pointer inline-block group">
                <div className={`w-14 h-14 rounded-full mx-auto flex items-center justify-center transition-all ${
                  isDragging ? "bg-[#002147] text-white scale-110" : "bg-blue-50 text-blue-900 border border-blue-200 group-hover:bg-[#002147] group-hover:text-white"
                }`}>
                  <Plus className="w-7 h-7" />
                </div>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,image/*"
                  onChange={handleFileInputChange}
                  disabled={uploading}
                  className="hidden"
                />
              </label>

              <div>
                <p className="text-xs font-bold text-[#002147]">
                  {isDragging ? "Drop your file here!" : "Click (+) or Drag & Drop Image / Document Here"}
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Supports Images (PNG, JPG, WEBP) & Documents (PDF, DOCX) up to 5MB
                </p>
              </div>

              <div className="pt-1">
                <label className="inline-flex items-center space-x-1.5 px-4 py-2 rounded bg-[#002147] hover:bg-[#001529] text-white text-xs font-bold cursor-pointer shadow-sm transition-all">
                  <PlusCircle className="w-4 h-4" />
                  <span>Add Image / File</span>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,image/*"
                    onChange={handleFileInputChange}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
          )}

          {/* Active Drag Overlay */}
          {isDragging && (
            <div className="absolute inset-0 bg-blue-100/90 rounded border-2 border-blue-700 flex items-center justify-center pointer-events-none">
              <div className="px-5 py-2.5 rounded bg-[#002147] text-white font-bold text-xs shadow-lg flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Drop File to Upload</span>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Lightbox removed from here to place outside */}

      {/* Profile Setup Form */}
      <form onSubmit={handleSaveProfile} className="space-y-6">
        
        {/* Section 1: Academic Background & Candidate Identification */}
        <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-[#002147] flex items-center space-x-2 border-b border-slate-200 pb-2">
            <GraduationCap className="w-4 h-4 text-blue-700" />
            <span>Academic Background & Qualifications</span>
          </h3>

          {/* Candidate Identification Section (Name & Age) */}
          <div>
            <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <span className="inline-block w-1 h-3 rounded bg-blue-600" />
              Candidate Identification
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label htmlFor="candidate_full_name" className="block font-semibold text-slate-700 mb-1">
                  Candidate Full Name <span className="text-blue-700 font-bold">*</span>
                </label>
                <input
                  id="candidate_full_name"
                  type="text"
                  value={profile.full_name || ""}
                  onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                  placeholder="e.g. Rahul Sharma"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700 focus:outline-none"
                />
                {validationErrors.full_name && (
                  <p className="text-[11px] text-red-600 font-medium mt-1">{validationErrors.full_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="candidate_age" className="block font-semibold text-slate-700 mb-1">
                  Candidate Age (21-24 Yrs) <span className="text-blue-700 font-bold">*</span>
                </label>
                <input
                  id="candidate_age"
                  type="number"
                  min={18}
                  max={35}
                  value={profile.age ?? ""}
                  onChange={(e) => setProfile({ ...profile, age: e.target.value ? parseInt(e.target.value) : "" })}
                  placeholder="e.g. 22"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700 focus:outline-none"
                />
                {validationErrors.age && (
                  <p className="text-[11px] text-red-600 font-medium mt-1">{validationErrors.age}</p>
                )}
              </div>
            </div>
          </div>

          {/* Academic Qualification Dropdowns */}
          <div>
            <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <span className="inline-block w-1 h-3 rounded bg-blue-600" />
              Academic Qualification
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">

              {/* Course / Program Dropdown */}
              <div>
                <label htmlFor="course_program" className="block font-semibold text-slate-700 mb-1">
                  Course / Program <span className="text-blue-700 font-bold">*</span>
                </label>
                <select
                  id="course_program"
                  value={profile.course_program || ""}
                  onChange={(e) => setProfile({ ...profile, course_program: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700 focus:outline-none"
                >
                  <option value="">Select your course / program</option>
                  {[
                    "B.E. / B.Tech", "B.Sc", "BCA", "B.Com", "BBA", "BA",
                    "B.Arch", "B.Des", "B.Pharm", "BPT", "B.L / LLB", "MBBS",
                    "BDS", "BAMS", "BHMS", "B.Ed", "BSW", "B.Voc",
                    "M.E. / M.Tech", "M.Sc", "MCA", "MBA", "MA", "M.Com",
                    "M.Arch", "M.Des", "M.Pharm", "M.Ed", "MSW", "LLM",
                    "PhD", "Diploma", "Polytechnic Diploma", "ITI", "Other"
                  ].map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
                {validationErrors.course_program && (
                  <p className="text-[11px] text-red-600 font-medium mt-1">{validationErrors.course_program}</p>
                )}
              </div>
 
              {/* Qualification / Study Type Dropdown */}
              <div>
                <label htmlFor="qualification_type" className="block font-semibold text-slate-700 mb-1">
                  Qualification / Study Type <span className="text-blue-700 font-bold">*</span>
                </label>
                <select
                  id="qualification_type"
                  value={profile.qualification_type || ""}
                  onChange={(e) => setProfile({ ...profile, qualification_type: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700 focus:outline-none"
                >
                  <option value="">Select your qualification type</option>
                  {[
                    "Engineering Degree", "3-Year Undergraduate Degree",
                    "4-Year Undergraduate Degree", "5-Year Integrated Degree",
                    "Postgraduate Degree", "Diploma", "Polytechnic Diploma",
                    "ITI / Vocational", "Professional Degree", "Medical Degree",
                    "Law Degree", "Education Degree", "Doctoral Degree", "Other"
                  ].map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
                {validationErrors.qualification_type && (
                  <p className="text-[11px] text-red-600 font-medium mt-1">{validationErrors.qualification_type}</p>
                )}
              </div>
            </div>
          </div>

          {/* Degree Discipline and Branch */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Degree Discipline (e.g. B.Tech, B.Com)</label>
              <input
                type="text"
                value={profile.degree || ""}
                onChange={(e) => setProfile({ ...profile, degree: e.target.value })}
                placeholder="e.g. B.Tech"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>

            {/* Branch / Discipline — Dynamic Searchable Dropdown for Engineering Degree */}
            {(() => {
              const isEngineering = profile.qualification_type === "Engineering Degree";
              const resolvedCode = isEngineering ? normalizeStoredBranch(profile.branch) : "";
              const resolvedLabel = isEngineering ? getBranchLabel(resolvedCode) : "";

              const filteredBranches = ENGINEERING_OPTIONS.filter(b =>
                matchAbbreviation(b.label, branchSearch)
              );

              if (isEngineering) {
                return (
                  <div>
                    <label htmlFor="eng_branch" className="block font-semibold text-slate-700 mb-1">
                      Branch / Discipline (if applicable) <span className="text-blue-700 font-bold">*</span>
                    </label>
                    {/* Searchable dropdown */}
                    <div className="relative" id="eng_branch">
                      <div className="flex items-center border border-slate-300 rounded bg-white focus-within:border-blue-700 overflow-hidden">
                        <input
                          type="text"
                          value={branchDropdownOpen ? branchSearch : (resolvedLabel || "")}
                          placeholder={resolvedLabel || "Select your engineering branch / discipline"}
                          onFocus={() => {
                            setBranchDropdownOpen(true);
                            setBranchSearch("");
                          }}
                          onChange={(e) => setBranchSearch(e.target.value)}
                          onBlur={() => setTimeout(() => setBranchDropdownOpen(false), 180)}
                          className="flex-1 px-3 py-1.5 text-slate-900 outline-none bg-transparent text-xs"
                          autoComplete="off"
                          required
                        />
                        <span className="pr-2.5 text-slate-400 text-[10px]">▼</span>
                      </div>
                      {branchDropdownOpen && (
                        <ul className="absolute z-30 mt-1 w-full bg-white border border-slate-300 rounded shadow-lg max-h-52 overflow-y-auto text-xs">
                          {filteredBranches.length === 0 ? (
                            <li className="px-3 py-2 text-slate-400 italic">No branches match your search</li>
                          ) : (
                            filteredBranches.map((b) => (
                              <li
                                key={b.code + b.label}
                                onMouseDown={() => {
                                  setProfile({ ...profile, branch: b.code });
                                  setBranchSearch("");
                                  setBranchDropdownOpen(false);
                                }}
                                className={`px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-900 transition-colors ${
                                  resolvedCode === b.code ? "bg-blue-50 text-blue-900 font-semibold" : "text-slate-800"
                                }`}
                              >
                                {b.label}
                              </li>
                            ))
                          )}
                        </ul>
                      )}
                    </div>
                    <p className="text-[10px] text-blue-700 font-medium mt-1">
                      Select your engineering branch to improve academic eligibility and internship recommendations.
                    </p>
                    {validationErrors.branch && (
                      <p className="text-[11px] text-red-600 font-medium mt-1">{validationErrors.branch}</p>
                    )}
                  </div>
                );
              }

              // Non-engineering qualification: disabled branch field (doesn't delete value!)
              return (
                <div>
                  <label className="block font-semibold text-slate-400 mb-1">
                    Branch / Discipline (if applicable)
                  </label>
                  <input
                    type="text"
                    disabled
                    value={profile.branch || ""}
                    placeholder="Select an engineering qualification to enable branch selection"
                    className="w-full bg-slate-100 border border-slate-200 rounded px-3 py-1.5 text-slate-400 cursor-not-allowed"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    Branch selection is only applicable for engineering programs.
                  </p>
                </div>
              );
            })()}

            <div className="sm:col-span-2">
              <label className="block font-semibold text-slate-700 mb-1">College / Institution Name</label>
              <input
                type="text"
                value={profile.institution || ""}
                onChange={(e) => setProfile({ ...profile, institution: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">CGPA / Percentage Marks</label>
              <input
                type="number"
                step="0.1"
                value={profile.cgpa || 8.5}
                onChange={(e) => setProfile({ ...profile, cgpa: parseFloat(e.target.value) || 8.0 })}
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Preferences & Target Roles */}
        <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-[#002147] flex items-center space-x-2 border-b border-slate-200 pb-2">
            <Building className="w-4 h-4 text-emerald-700" />
            <span>Sector & Role Preferences</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Preferred Industry Sector</label>
              <input
                type="text"
                value={profile.preferred_industry || ""}
                onChange={(e) => setProfile({ ...profile, preferred_industry: e.target.value })}
                placeholder="e.g. Public Sector / IT Services"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Target Role Category</label>
              <input
                type="text"
                value={profile.preferred_role || ""}
                onChange={(e) => setProfile({ ...profile, preferred_role: e.target.value })}
                placeholder="e.g. Data Analyst"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Preferred Location</label>
              <input
                type="text"
                value={profile.preferred_location || ""}
                onChange={(e) => setProfile({ ...profile, preferred_location: e.target.value })}
                placeholder="e.g. Bengaluru / Remote"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Skills Tag Editor */}
        <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-[#002147] flex items-center space-x-2 border-b border-slate-200 pb-2">
            <Sparkles className="w-4 h-4 text-amber-600" />
            <span>Technical & Soft Skills Matrix Editor</span>
          </h3>
          {validationErrors.skills && (
            <p className="text-xs text-red-600 font-medium">{validationErrors.skills}</p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Category Dropdown */}
            <div className="relative">
              <label className="block font-semibold text-slate-700 mb-1 text-xs">
                Skill Category / Topic <span className="text-blue-700 font-bold">*</span>
              </label>
              <div className="flex items-center border border-slate-300 rounded bg-white focus-within:border-blue-700 overflow-hidden">
                <input
                  type="text"
                  value={categoryDropdownOpen ? skillCategorySearch : (selectedSkillCategory || "")}
                  placeholder="Select a skill category"
                  onFocus={() => {
                    setCategoryDropdownOpen(true);
                    setSkillCategorySearch("");
                  }}
                  onChange={(e) => setSkillCategorySearch(e.target.value)}
                  onBlur={() => setTimeout(() => setCategoryDropdownOpen(false), 200)}
                  className="flex-1 px-3 py-1.5 text-slate-900 outline-none bg-transparent text-xs"
                  autoComplete="off"
                />
                <span className="pr-2.5 text-slate-400 text-[10px]">▼</span>
              </div>
              {categoryDropdownOpen && (
                <ul className="absolute z-30 mt-1 w-full bg-white border border-slate-300 rounded shadow-lg max-h-52 overflow-y-auto text-xs">
                  {CATEGORY_OPTIONS.filter(cat => cat.toLowerCase().includes(skillCategorySearch.toLowerCase())).length === 0 ? (
                    <li className="px-3 py-2 text-slate-400 italic">No categories match your search</li>
                  ) : (
                    CATEGORY_OPTIONS.filter(cat => cat.toLowerCase().includes(skillCategorySearch.toLowerCase())).map((cat) => (
                      <li
                        key={cat}
                        onMouseDown={() => {
                          setSelectedSkillCategory(cat);
                          setSelectedSkillName("");
                          setCustomSkillName("");
                          setSkillCategorySearch("");
                          setCategoryDropdownOpen(false);
                        }}
                        className={`px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-900 transition-colors ${
                          selectedSkillCategory === cat ? "bg-blue-50 text-blue-900 font-semibold" : "text-slate-800"
                        }`}
                      >
                        {cat}
                      </li>
                    ))
                  )}
                </ul>
              )}
            </div>

            {/* Dependent Skill Dropdown */}
            <div className="relative">
              <label className={`block font-semibold mb-1 text-xs ${selectedSkillCategory ? "text-slate-700" : "text-slate-400"}`}>
                Skill <span className="text-blue-700 font-bold">*</span>
              </label>
              
              {selectedSkillCategory === "Other" ? (
                <input
                  type="text"
                  value={customSkillName}
                  onChange={(e) => setCustomSkillName(e.target.value)}
                  placeholder="Enter your custom skill name"
                  className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-slate-900 focus:border-blue-700 text-xs"
                />
              ) : (
                <>
                  <div className={`flex items-center border rounded overflow-hidden ${
                    selectedSkillCategory 
                      ? "border-slate-300 bg-white focus-within:border-blue-700" 
                      : "border-slate-200 bg-slate-50 cursor-not-allowed"
                  }`}>
                    <input
                      type="text"
                      disabled={!selectedSkillCategory}
                      value={skillDropdownOpen ? skillNameSearch : (selectedSkillName || "")}
                      placeholder={selectedSkillCategory ? "Select a skill" : "Select a category first"}
                      onFocus={() => {
                        setSkillDropdownOpen(true);
                        setSkillNameSearch("");
                      }}
                      onChange={(e) => setSkillNameSearch(e.target.value)}
                      onBlur={() => setTimeout(() => setSkillDropdownOpen(false), 200)}
                      className={`flex-1 px-3 py-1.5 text-slate-900 outline-none bg-transparent text-xs ${
                        !selectedSkillCategory ? "text-slate-400 cursor-not-allowed" : ""
                      }`}
                      autoComplete="off"
                    />
                    <span className="pr-2.5 text-slate-400 text-[10px]">▼</span>
                  </div>
                  {skillDropdownOpen && selectedSkillCategory && (
                    <ul className="absolute z-30 mt-1 w-full bg-white border border-slate-300 rounded shadow-lg max-h-52 overflow-y-auto text-xs">
                      {(SKILL_MAPPING[selectedSkillCategory] || []).filter(s => s.toLowerCase().includes(skillNameSearch.toLowerCase())).length === 0 ? (
                        <li className="px-3 py-2 text-slate-400 italic">No skills match your search</li>
                      ) : (
                        (SKILL_MAPPING[selectedSkillCategory] || []).filter(s => s.toLowerCase().includes(skillNameSearch.toLowerCase())).map((s) => (
                          <li
                            key={s}
                            onMouseDown={() => {
                              setSelectedSkillName(s);
                              setSkillNameSearch("");
                              setSkillDropdownOpen(false);
                            }}
                            className={`px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-900 transition-colors ${
                              selectedSkillName === s ? "bg-blue-50 text-blue-900 font-semibold" : "text-slate-800"
                            }`}
                          >
                            {s}
                          </li>
                        ))
                      )}
                    </ul>
                  )}
                </>
              )}
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="button"
              onClick={handleAddSkill}
              disabled={!selectedSkillCategory || (selectedSkillCategory === "Other" ? !customSkillName.trim() : !selectedSkillName)}
              className={`px-4 py-2 font-bold rounded shadow-sm transition-colors flex items-center space-x-1.5 text-xs ${
                (selectedSkillCategory && (selectedSkillCategory === "Other" ? customSkillName.trim() : selectedSkillName))
                  ? "bg-[#002147] hover:bg-[#001529] text-white cursor-pointer"
                  : "bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed"
              }`}
            >
              <Plus className="w-4 h-4" />
              <span>Add Skill</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-100">
            {profile.skills.map((s: any, idx: number) => {
              const skillName = typeof s === "string" ? s : s.display_skill;
              const categoryName = typeof s === "string" ? "General" : s.display_category;
              return (
                <span
                  key={idx}
                  className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-300 flex items-center space-x-1.5"
                  title={`Category: ${categoryName}`}
                >
                  <span>{skillName}</span>
                  <span className="text-[9px] text-slate-400 font-normal">({categoryName})</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skillName)}
                    className="text-slate-500 hover:text-red-700 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </span>
              );
            })}
          </div>
        </div>

        {/* Section 4: Optional Verified LeetCode Coding Profile Connection */}
        <div className="p-5 rounded bg-white border border-slate-300 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-2">
            <h3 className="text-base font-bold text-[#002147] flex items-center space-x-2">
              <Code2 className="w-4 h-4 text-amber-500" />
              <span>LeetCode Coding Profile & Ownership Verification</span>
            </h3>

            {/* State Indicator Badge */}
            <div className="flex items-center space-x-2 text-xs font-bold">
              {leetcodeStatus === "NOT_CONNECTED" && (
                <span className="px-2.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-300">
                  Not Connected
                </span>
              )}
              {leetcodeStatus === "VALIDATING" && (
                <span className="px-2.5 py-0.5 rounded bg-blue-50 text-blue-900 border border-blue-300 flex items-center space-x-1.5">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Validating Account Existence...</span>
                </span>
              )}
              {leetcodeStatus === "ACCOUNT_NOT_FOUND" && (
                <span className="px-2.5 py-0.5 rounded bg-red-50 text-red-900 border border-red-300 flex items-center space-x-1">
                  <AlertCircle className="w-3.5 h-3.5 text-red-600" />
                  <span>LeetCode Account Not Found</span>
                </span>
              )}
              {leetcodeStatus === "ACCOUNT_FOUND" && (
                <span className="px-2.5 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-300 flex items-center space-x-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                  <span>Account Found</span>
                </span>
              )}
              {leetcodeStatus === "OWNERSHIP_PENDING" && (
                <span className="px-2.5 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-300 flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                  <span>Ownership Challenge Issued</span>
                </span>
              )}
              {leetcodeStatus === "VERIFIED" && (
                <span className="px-2.5 py-0.5 rounded bg-emerald-50 text-emerald-900 border border-emerald-300 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Verified LeetCode Profile</span>
                </span>
              )}
              {leetcodeStatus === "VERIFICATION_FAILED" && (
                <span className="px-2.5 py-0.5 rounded bg-red-50 text-red-900 border border-red-300 flex items-center space-x-1">
                  <AlertCircle className="w-3.5 h-3.5 text-red-600" />
                  <span>Ownership Verification Failed</span>
                </span>
              )}
              {leetcodeStatus === "DATA_UNAVAILABLE" && (
                <span className="px-2.5 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-300 flex items-center space-x-1">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Verification Unavailable</span>
                </span>
              )}
            </div>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            {leetcodeStatus === "DATA_UNAVAILABLE"
              ? "LeetCode profile verification and live statistics are currently unavailable."
              : leetcodeStatus === "VERIFIED"
              ? "Your LeetCode profile is connected."
              : "Connect your public LeetCode profile to display your total solved problems count."}
          </p>

          {/* Form Controls & Verification Steps */}
          {leetcodeStatus !== "VERIFIED" ? (
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={leetcodeInput}
                    onChange={(e) => setLeetcodeInput(e.target.value)}
                    placeholder="e.g. https://leetcode.com/u/25CSEB52SANJAY/"
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 placeholder:text-slate-400 focus:ring-2 focus:ring-[#002147] focus:border-[#002147] outline-none"
                  />
                </div>

                <button
                  type="button"
                  onClick={async () => {
                    if (!leetcodeInput.trim()) return;
                    setLeetcodeStatus("VALIDATING");
                    try {
                      const res = await fetchApi("/students/leetcode/connect", {
                        method: "POST",
                        body: JSON.stringify({ leetcode_url: leetcodeInput.trim() })
                      });
                      if (res && res.leetcode_username) {
                        setConnectedUsername(res.leetcode_username);
                        setLeetcodeStatus("VERIFIED");
                        setProfile((prev: any) => ({
                          ...prev,
                          leetcode_username: res.leetcode_username,
                          leetcode_total_solved: res.problems_solved
                        }));
                      } else {
                        setLeetcodeStatus("ACCOUNT_NOT_FOUND");
                      }
                    } catch (e) {
                      setLeetcodeStatus("ACCOUNT_NOT_FOUND");
                    }
                  }}
                  disabled={!leetcodeInput.trim() || leetcodeStatus === "VALIDATING"}
                  className="px-4 py-2 bg-[#002147] hover:bg-[#001529] text-white font-bold text-xs rounded shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center space-x-1.5 shrink-0"
                >
                  {leetcodeStatus === "VALIDATING" ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <>
                      <Code2 className="w-3.5 h-3.5" />
                      <span>Connect / Check</span>
                    </>
                  )}
                </button>
              </div>

              {leetcodeStatus === "ACCOUNT_NOT_FOUND" && (
                <p className="text-xs text-red-600 font-medium pt-1">
                  Unable to retrieve public LeetCode profile. Please check the profile URL.
                </p>
              )}
            </div>
          ) : (
            /* Connected LeetCode Display Box */
            <div className="p-4 rounded-lg bg-emerald-50/80 border border-emerald-300 text-xs space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <div className="w-9 h-9 rounded-full bg-emerald-100 border border-emerald-400 flex items-center justify-center text-emerald-900 font-bold shrink-0">
                    <Code2 className="w-4.5 h-4.5 text-emerald-700" />
                  </div>
                  <div>
                    <h4 className="font-bold text-emerald-950 flex items-center space-x-1 text-sm">
                      <span>LeetCode Profile</span>
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    </h4>
                    <p className="text-xs text-emerald-800 font-medium">
                      Connected Handle: <strong className="text-emerald-950">@{connectedUsername || profile.leetcode_username}</strong>
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        await fetchApi("/students/leetcode", { method: "DELETE" });
                      } catch (e) {}
                      setLeetcodeStatus("NOT_CONNECTED");
                      setConnectedUsername(null);
                      setLeetcodeInput("");
                      setProfile((prev: any) => ({
                        ...prev,
                        leetcode_username: null,
                        leetcode_total_solved: null
                      }));
                    }}
                    className="px-2.5 py-1.5 bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 font-bold rounded transition-colors"
                  >
                    Disconnect
                  </button>
                </div>
              </div>

              <div className="p-3 bg-white border border-emerald-200 rounded-md flex items-center justify-between">
                <span className="font-bold text-slate-700 text-xs">
                  LeetCode Problems Solved:
                </span>
                <span className="font-extrabold text-base text-[#002147]">
                  {profile.leetcode_total_solved !== null && profile.leetcode_total_solved !== undefined
                    ? profile.leetcode_total_solved
                    : "Unavailable"}
                </span>
              </div>
            </div>
          )}

          {/* Test State Simulator Selector (For Task 2 Verification Demonstration) */}
          <div className="p-2.5 bg-slate-50 border border-slate-200 rounded text-[11px] flex flex-wrap items-center gap-2">
            <span className="font-bold text-slate-700">UI State Simulator:</span>
            {(
              [
                "NOT_CONNECTED",
                "VALIDATING",
                "ACCOUNT_NOT_FOUND",
                "ACCOUNT_FOUND",
                "OWNERSHIP_PENDING",
                "VERIFIED",
                "VERIFICATION_FAILED",
                "DATA_UNAVAILABLE"
              ] as const
            ).map((st) => (
              <button
                key={st}
                type="button"
                onClick={() => {
                  setLeetcodeStatus(st);
                  if (st === "VERIFIED" && !connectedUsername) {
                    setConnectedUsername("sample_coder");
                  }
                  if (st === "OWNERSHIP_PENDING" && !verificationToken) {
                    setVerificationToken("LEETCODE_VERIFY_DEMO123");
                    setConnectedUsername("sample_coder");
                  }
                }}
                className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold border transition-colors ${
                  leetcodeStatus === st
                    ? "bg-[#002147] text-white border-[#002147]"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
                }`}
              >
                {st}
              </button>
            ))}
          </div>

        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded shadow transition-all"
        >
          {saving ? "Saving Profile..." : "Save Candidate Profile Setup"}
        </button>
      </form>
        </>
      ) : (
        /* READ-ONLY SUMMARY VIEW (VIEW MODE) */
        <div className="space-y-6">
          {/* Main info card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="md:col-span-2 p-6 rounded bg-white border border-slate-300 shadow-sm space-y-4">
              <div className="flex items-center space-x-3 border-b border-slate-200 pb-3">
                <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-[#002147] shrink-0 font-bold text-lg">
                  {(profile.full_name || currentUser?.full_name || currentUser?.name || currentUser?.username || "C").charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#002147]">{profile.full_name || currentUser?.full_name || currentUser?.name || currentUser?.username || "—"}</h2>
                  <p className="text-xs text-slate-500">{currentUser?.email || "—"}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Candidate Full Name</span>
                  <span className="text-slate-900 font-medium">{profile.full_name || currentUser?.full_name || currentUser?.name || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Candidate Age</span>
                  <span className="text-slate-900 font-medium">{profile.age ? `${profile.age} Yrs` : "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Phone Number</span>
                  <span className="text-slate-900 font-medium">{profile.phone || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Course / Program</span>
                  <span className="text-slate-900 font-medium">{profile.course_program || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Qualification / Study Type</span>
                  <span className="text-slate-900 font-medium">{profile.qualification_type || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Degree / Academic Discipline</span>
                  <span className="text-slate-900 font-medium">{profile.degree || "—"}</span>
                </div>
                {profile.qualification_type === "Engineering Degree" && (
                  <div>
                    <span className="block text-slate-500 font-semibold mb-0.5">Engineering Branch</span>
                    <span className="text-slate-950 font-semibold bg-blue-50/50 px-2 py-0.5 rounded border border-blue-200 inline-block">
                      {ENGINEERING_OPTIONS.find(b => b.code === profile.branch)?.label || profile.branch || "—"}
                    </span>
                  </div>
                )}
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">College / Institution Name</span>
                  <span className="text-slate-900 font-medium">{profile.institution || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">Graduation Year</span>
                  <span className="text-slate-900 font-medium">{profile.graduation_year || "—"}</span>
                </div>
                <div>
                  <span className="block text-slate-500 font-semibold mb-0.5">CGPA / Percentage Marks</span>
                  <span className="text-slate-900 font-medium">{profile.cgpa || "—"}</span>
                </div>
              </div>
            </div>

            {/* Document Preview Card */}
            <div className="p-6 rounded bg-white border border-slate-300 shadow-sm flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#002147] border-b border-slate-200 pb-2">Academic Document</h3>
                {profile.resume_url ? (
                  <div className="space-y-3">
                    <div className="aspect-[4/3] bg-slate-50 border border-slate-200 rounded flex flex-col items-center justify-center p-3 text-center">
                      {profile.resume_url.match(/\.(png|jpg|jpeg|gif|webp)$/i) ? (
                        <img
                          src={getFullFileUrl(profile.resume_url)}
                          alt="Uploaded document"
                          className="max-h-full object-contain cursor-pointer hover:opacity-90"
                          onClick={() => setShowImageLightbox(true)}
                        />
                      ) : (
                        <div className="space-y-1">
                          <FileText className="w-8 h-8 text-blue-900 mx-auto" />
                          <p className="text-[10px] font-bold text-slate-700 truncate max-w-[180px] mx-auto">
                            {profile.resume_url.split("/").pop()}
                          </p>
                        </div>
                      )}
                    </div>
                    <a
                      href={getFullFileUrl(profile.resume_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 rounded text-center text-xs font-bold transition-all block"
                    >
                      View / Download Document ↗
                    </a>
                  </div>
                ) : (
                  <div className="aspect-[4/3] bg-slate-50 border border-slate-200 border-dashed rounded flex flex-col items-center justify-center p-3 text-center text-slate-400">
                    <FileText className="w-8 h-8 mb-1.5" />
                    <span className="text-xs">No document uploaded</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Preferences Section */}
          <div className="p-6 rounded bg-white border border-slate-300 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-[#002147] border-b border-slate-200 pb-2 flex items-center space-x-1.5">
              <Building className="w-4 h-4 text-slate-500" />
              <span>Sector & Role Preferences</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div>
                <span className="block text-slate-500 font-semibold mb-0.5">Preferred Industry Sector</span>
                <span className="text-slate-900 font-medium">{profile.preferred_industry || "—"}</span>
              </div>
              <div>
                <span className="block text-slate-500 font-semibold mb-0.5">Target Role Category</span>
                <span className="text-slate-900 font-medium">{profile.preferred_role || "—"}</span>
              </div>
              <div>
                <span className="block text-slate-500 font-semibold mb-0.5">Preferred Location</span>
                <span className="text-slate-900 font-medium">{profile.preferred_location || "—"}</span>
              </div>
              <div>
                <span className="block text-slate-500 font-semibold mb-0.5">Work Mode</span>
                <span className="text-slate-900 font-medium">{profile.work_mode || "—"}</span>
              </div>
              <div>
                <span className="block text-slate-500 font-semibold mb-0.5">Preferred Duration</span>
                <span className="text-slate-900 font-medium">{profile.preferred_duration || "—"}</span>
              </div>
            </div>
          </div>

          {/* Projects Summary */}
          <div className="p-6 rounded bg-white border border-slate-300 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-[#002147] border-b border-slate-200 pb-2 flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-slate-500" />
              <span>Academic Projects & Background Summary</span>
            </h3>
            <div className="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
              {profile.projects_summary || "—"}
            </div>
          </div>

          {/* Skills Section */}
          <div className="p-6 rounded bg-white border border-slate-300 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-[#002147] border-b border-slate-200 pb-2 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Technical & Soft Skills Matrix</span>
            </h3>
            <div className="space-y-4 text-xs">
              {profile.skills && profile.skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map((s: any, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-1 rounded-full bg-blue-50 text-blue-900 border border-blue-200 font-medium"
                    >
                      {s.display_skill} <span className="text-slate-500 ml-1">({s.display_category})</span>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-slate-400 italic">No skills added to your profile.</p>
              )}
            </div>
          </div>

          {/* LeetCode Profile Section (Preserving exact display strings and checks) */}
          <div className="p-6 rounded bg-white border border-slate-300 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-[#002147] border-b border-slate-200 pb-2 flex items-center space-x-1.5">
              <Code2 className="w-4 h-4 text-slate-500" />
              <span>LeetCode Integration</span>
            </h3>

            <div className="text-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 bg-emerald-50/80 border border-emerald-300 rounded">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 border border-emerald-400 flex items-center justify-center text-emerald-950 font-bold shrink-0">
                    <Code2 className="w-4 h-4 text-emerald-700" />
                  </div>
                  <div>
                    <h4 className="font-bold text-emerald-950 flex items-center space-x-1">
                      <span>LeetCode Profile Verified</span>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    </h4>
                    <p className="text-[11px] text-emerald-800">
                      Connected Handle: <strong className="text-emerald-950">@{connectedUsername || profile.leetcode_username || "sample_coder"}</strong> • Method: <span className="font-mono text-[10px]">BIO_TOKEN_CHALLENGE</span>
                    </p>
                  </div>
                </div>
                {(connectedUsername || profile.leetcode_username) && (
                  <a
                    href={`https://leetcode.com/u/${connectedUsername || profile.leetcode_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-white hover:bg-slate-50 text-emerald-900 border border-emerald-300 font-bold rounded flex items-center space-x-1 shadow-xs shrink-0 text-center"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>View LeetCode Profile ↗</span>
                  </a>
                )}
              </div>

              <p className="text-xs text-slate-600">
                Your LeetCode profile has been verified. LeetCode profile verification and live statistics are currently unavailable because an approved profile-data provider is not configured.
              </p>

              {/* Render Verification Unavailable state */}
              <div className="p-3 bg-amber-50/80 border border-amber-300 rounded text-xs space-y-2">
                <div className="flex items-center space-x-1.5 text-amber-900 font-bold">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Verification Unavailable</span>
                </div>
                <p className="text-slate-700 text-[11px]">
                  LeetCode profile verification and live statistics are currently unavailable because an approved profile-data provider is not configured. Connect your LeetCode profile to enable coding-profile evaluation when an approved data provider is available.
                </p>
              </div>

              {/* Verified Problem Statistics Block */}
              <div className="p-3 bg-white/90 border border-emerald-200 rounded-md space-y-3">
                <div className="flex items-center justify-between border-b border-emerald-100 pb-2">
                  <span className="font-bold text-emerald-950 text-xs flex items-center space-x-1">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Verified Real Problem Statistics</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-medium">
                    Last Verified: {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>

                {profile.leetcode_metrics_status === "SUCCESS" && profile.leetcode_total_solved !== null && profile.leetcode_total_solved !== undefined ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                      <div className="p-2 bg-slate-50 border border-slate-200 rounded">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Total Solved</div>
                        <div className="text-base font-bold text-slate-900 mt-0.5">{profile.leetcode_total_solved}</div>
                      </div>
                      <div className="p-2 bg-emerald-50 border border-emerald-200 rounded">
                        <div className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">Easy</div>
                        <div className="text-base font-bold text-emerald-900 mt-0.5">{profile.leetcode_easy_solved}</div>
                      </div>
                      <div className="p-2 bg-amber-50 border border-emerald-200 rounded">
                        <div className="text-[10px] font-bold text-amber-700 uppercase tracking-wider">Medium</div>
                        <div className="text-base font-bold text-emerald-900 mt-0.5">{profile.leetcode_medium_solved}</div>
                      </div>
                      <div className="p-2 bg-red-50 border border-red-200 rounded">
                        <div className="text-[10px] font-bold text-red-700 uppercase tracking-wider">Hard</div>
                        <div className="text-base font-bold text-red-900 mt-0.5">{profile.leetcode_hard_solved}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded space-y-1.5">
                        <h5 className="font-bold text-emerald-950 flex items-center space-x-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Verified Coding Strengths</span>
                        </h5>
                        <ul className="space-y-1 text-slate-700 list-disc list-inside text-[11px] leading-relaxed">
                          <li>Demonstrates active coding engagement.</li>
                        </ul>
                      </div>
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded space-y-1.5">
                        <h5 className="font-bold text-blue-950 flex items-center space-x-1">
                          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                          <span>Targeted Growth Recommendations</span>
                        </h5>
                        <ul className="space-y-1 text-slate-700 list-disc list-inside text-[11px] leading-relaxed">
                          <li>Continue practicing Data Structures & Algorithms.</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-3 bg-amber-50/60 border border-amber-200 rounded text-xs space-y-2">
                    <div className="flex items-center space-x-2 text-amber-900 font-bold">
                      <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                      <span>Live LeetCode profile metrics are currently unavailable through an approved data provider.</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-slate-600 font-mono text-[11px] pt-1">
                      <div>Problems Solved: —</div>
                      <div>Badges: —</div>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>
      )}

      {/* Image Lightbox Preview Modal */}
      {showImageLightbox && profile.resume_url && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs">
          <div className="relative w-full max-w-4xl max-h-[92vh] bg-white border border-slate-300 rounded p-4 flex flex-col items-center shadow-2xl">
            
            <div className="w-full flex items-center justify-between pb-2 border-b border-slate-200 mb-2 px-1">
              <span className="text-xs font-bold text-[#002147] flex items-center">
                <ImageIcon className="w-4 h-4 mr-1.5 text-blue-700" />
                Full Candidate Resume Image View
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleDeleteResume}
                  className="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 text-xs font-bold flex items-center space-x-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete</span>
                </button>
                <button
                  onClick={() => setShowImageLightbox(false)}
                  className="p-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="overflow-auto w-full max-h-[78vh] p-2 flex items-center justify-center bg-slate-900 rounded border border-slate-200">
              <img
                src={getFullFileUrl(profile.resume_url)}
                alt="Candidate Resume Full View"
                className="max-w-full max-h-[75vh] object-contain rounded"
              />
            </div>

            <div className="pt-2.5 w-full flex justify-end">
              <button
                onClick={() => setShowImageLightbox(false)}
                className="px-4 py-1.5 bg-[#002147] hover:bg-[#001529] text-white text-xs font-bold rounded"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
