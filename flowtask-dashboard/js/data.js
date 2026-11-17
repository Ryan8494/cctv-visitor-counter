/**
 * data.js — FlowTask Dummy Data & State Management
 * Exact match to DESIGN.md specifications (May 1 - 31, 2025; Today: Wed, May 14)
 */

const initialData = {
  user: {
    name: "Sarah Miller",
    role: "Product Manager",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=120&auto=format&fit=crop&q=80",
    greeting: "Good morning, Sarah! 👋",
    subtext: "Here's what's happening with your projects today.",
    dateRange: "May 1, 2025 – May 31, 2025"
  },

  kpis: [
    {
      id: "active-projects",
      title: "Active Projects",
      value: "12",
      trend: "↑ 25%",
      trendType: "positive",
      trendLabel: "vs last month",
      color: "var(--color-primary)",
      icon: "folder"
    },
    {
      id: "tasks-completed",
      title: "Tasks Completed",
      value: "186",
      trend: "↑ 18%",
      trendType: "positive",
      trendLabel: "vs last month",
      color: "var(--color-success)",
      icon: "check-circle"
    },
    {
      id: "pending-tasks",
      title: "Pending Tasks",
      value: "48",
      trend: "↓ 12%",
      trendType: "negative",
      trendLabel: "vs last month",
      color: "var(--color-warning)",
      icon: "clock"
    },
    {
      id: "team-members",
      title: "Team Members",
      value: "8",
      trend: "↑ 0%",
      trendType: "neutral",
      trendLabel: "Active this month",
      color: "var(--color-info-purple)",
      icon: "users"
    }
  ],

  projects: [
    {
      id: "proj-1",
      name: "Website Redesign",
      progress: 78,
      color: "#2563EB",
      bgTint: "#EAF1FE",
      icon: "globe"
    },
    {
      id: "proj-2",
      name: "Mobile App Development",
      progress: 62,
      color: "#7C5CE0",
      bgTint: "#F3E8FF",
      icon: "smartphone"
    },
    {
      id: "proj-3",
      name: "CRM Integration",
      progress: 45,
      color: "#22C58B",
      bgTint: "#E7F8F0",
      icon: "database"
    },
    {
      id: "proj-4",
      name: "Marketing Campaign",
      progress: 90,
      color: "#F5A524",
      bgTint: "#FEF4DC",
      icon: "megaphone"
    }
  ],

  tasksOverview: {
    total: 248,
    segments: [
      { label: "Completed", value: 186, color: "#1D4ED8" },
      { label: "In Progress", value: 48, color: "#6EA0F5" },
      { label: "To Do", value: 14, color: "#C9D8F8" }
    ]
  },

  weekDays: [
    { day: "Mon", date: 12, hasEvent: false, isToday: false },
    { day: "Tue", date: 13, hasEvent: true, isToday: false },
    { day: "Wed", date: 14, hasEvent: true, isToday: true },
    { day: "Thu", date: 15, hasEvent: true, isToday: false },
    { day: "Fri", date: 16, hasEvent: true, isToday: false },
    { day: "Sat", date: 17, hasEvent: false, isToday: false },
    { day: "Sun", date: 18, hasEvent: false, isToday: false }
  ],

  agendaEvents: [
    {
      id: "event-1",
      title: "Design Review",
      time: "10:00 AM – 11:00 AM",
      color: "#EF4444",
      attendees: [
        { name: "Sarah Miller", avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80" },
        { name: "James Wilson", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80" }
      ]
    },
    {
      id: "event-2",
      title: "Sprint Planning",
      time: "1:00 PM – 2:00 PM",
      color: "#F5A524",
      attendees: [
        { name: "Sarah Miller", avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80" },
        { name: "Michael Chen", avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80" },
        { name: "Emily Davis", avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&auto=format&fit=crop&q=80" }
      ]
    },
    {
      id: "event-3",
      title: "Client Feedback",
      time: "3:00 PM – 4:00 PM",
      color: "#7C5CE0",
      attendees: [
        { name: "Sarah Miller", avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80" },
        { name: "James Wilson", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80" }
      ],
      extraCount: 2
    }
  ],

  teamMembers: [
    {
      id: "member-1",
      name: "Sarah Miller",
      role: "Product Manager",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80",
      status: "Online",
      statusClass: "online"
    },
    {
      id: "member-2",
      name: "James Wilson",
      role: "UI/UX Designer",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80",
      status: "In a meeting",
      statusClass: "meeting"
    },
    {
      id: "member-3",
      name: "Emily Davis",
      role: "Frontend Developer",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&auto=format&fit=crop&q=80",
      status: "Online",
      statusClass: "online"
    },
    {
      id: "member-4",
      name: "Michael Chen",
      role: "Backend Developer",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80",
      status: "Away",
      statusClass: "away"
    },
    {
      id: "member-5",
      name: "Olivia Brown",
      role: "QA Engineer",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80",
      status: "Online",
      statusClass: "online"
    }
  ],

  activityChart: {
    days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    series: [
      { name: "Completed", color: "#1D4ED8", data: [18, 22, 28, 24, 30, 12, 8] },
      { name: "In Progress", color: "#6EA0F5", data: [10, 8, 7, 9, 6, 4, 2] },
      { name: "Created", color: "#C9D8F8", data: [6, 5, 4, 5, 3, 2, 1] }
    ]
  },

  kanbanColumns: [
    {
      id: "todo",
      title: "To Do",
      tint: "var(--tint-neutral)",
      borderTint: "#DDE3ED",
      tasks: [
        {
          id: "task-101",
          title: "Research competitor features & pricing",
          priority: "Medium",
          date: "May 18",
          assignee: {
            name: "James Wilson",
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-102",
          title: "Draft API specification for v2.0",
          priority: "High",
          date: "May 19",
          assignee: {
            name: "Michael Chen",
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-103",
          title: "Prepare Q2 product roadmap slide deck",
          priority: "Low",
          date: "May 22",
          assignee: {
            name: "Sarah Miller",
            avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-104",
          title: "Setup automated end-to-end test suite",
          priority: "Medium",
          date: "May 24",
          assignee: {
            name: "Olivia Brown",
            avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
          }
        }
      ]
    },
    {
      id: "in-progress",
      title: "In Progress",
      tint: "var(--color-primary-50)",
      borderTint: "#C8DBFB",
      tasks: [
        {
          id: "task-201",
          title: "Redesign user onboarding flow",
          priority: "High",
          date: "May 16",
          assignee: {
            name: "James Wilson",
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-202",
          title: "Implement OAuth2 login with Google",
          priority: "High",
          date: "May 17",
          assignee: {
            name: "Emily Davis",
            avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-203",
          title: "Database schema migration for billing",
          priority: "Medium",
          date: "May 18",
          assignee: {
            name: "Michael Chen",
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80"
          }
        }
      ]
    },
    {
      id: "review",
      title: "Review",
      tint: "var(--tint-warning)",
      borderTint: "#F8E5B4",
      tasks: [
        {
          id: "task-301",
          title: "Checkout page payment gateway integration",
          priority: "High",
          date: "May 15",
          assignee: {
            name: "Emily Davis",
            avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-302",
          title: "Refactor navigation header & mobile drawer",
          priority: "Medium",
          date: "May 15",
          assignee: {
            name: "James Wilson",
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80"
          }
        }
      ]
    },
    {
      id: "done",
      title: "Done",
      tint: "var(--tint-success)",
      borderTint: "#C2EED7",
      tasks: [
        {
          id: "task-401",
          title: "User interview recordings & synthesis",
          isDone: true,
          date: "May 12",
          assignee: {
            name: "Sarah Miller",
            avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-402",
          title: "Design system token documentation",
          isDone: true,
          date: "May 13",
          assignee: {
            name: "James Wilson",
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80"
          }
        },
        {
          id: "task-403",
          title: "Security audit vulnerability patch",
          isDone: true,
          date: "May 14",
          assignee: {
            name: "Michael Chen",
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80"
          }
        }
      ]
    }
  ]
};
