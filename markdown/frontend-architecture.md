# 🖥️ Frontend Architecture
## Enterprise Insights Copilot - Next.js Frontend Implementation

### 🏗️ Architecture Overview

The frontend follows a **modern React architecture** with Next.js 14 App Router, implementing clean separation of concerns and scalable patterns.

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with providers
│   │   ├── page.tsx           # Home page
│   │   ├── globals.css        # Global styles
│   │   └── (routes)/          # Route groups
│   ├── components/            # React components
│   │   ├── ui/               # Reusable UI components
│   │   ├── providers/        # Context providers
│   │   ├── forms/            # Form components
│   │   └── layout/           # Layout components
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utility libraries
│   │   ├── api-client.ts     # API communication
│   │   ├── query-client.ts   # React Query setup
│   │   ├── schemas.ts        # Zod validation schemas
│   │   └── utils.ts          # Helper functions
│   ├── types/                # TypeScript type definitions
│   └── styles/               # Additional stylesheets
```

---

## 🔧 Technology Stack

### Core Framework
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety and better developer experience
- **React 18**: Latest React features (Suspense, Concurrent features)

### State Management
- **React Query (TanStack Query)**: Server state management
- **React Hooks**: Local component state
- **Context API**: Global UI state (theme, user preferences)

### Styling & UI
- **Tailwind CSS**: Utility-first CSS framework
- **CSS Variables**: Design tokens and theming
- **Framer Motion**: Animations and transitions
- **Lucide React**: Consistent icon library

### Data & Validation
- **Zod**: Runtime type validation
- **Axios**: HTTP client with interceptors
- **React Hook Form**: Form handling and validation

---

## 🧩 Component Architecture

### Component Hierarchy
```tsx
// Root Layout
<QueryProvider>
  <ThemeProvider>
    <Layout>
      <Header>
        <HealthIndicator />
        <NavigationMenu />
      </Header>
      <Main>
        <ModernDashboard>
          <TabNavigation />
          <TabContent>
            {/* Route-specific content */}
          </TabContent>
        </ModernDashboard>
      </Main>
      <Footer />
    </Layout>
  </ThemeProvider>
</QueryProvider>
```

### Component Types

#### 1. UI Components (`/components/ui/`)
```tsx
// Reusable, unstyled components
export interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ ... }) => {
  // Implementation
};
```

#### 2. Feature Components (`/components/`)
```tsx
// Feature-specific components
export const FileUploadQueue: React.FC<FileUploadQueueProps> = () => {
  const uploadMutation = useFileUpload();
  // Component logic
};
```

#### 3. Layout Components (`/components/layout/`)
```tsx
// Layout and structural components
export const DashboardLayout: React.FC<{ children: React.ReactNode }> = () => {
  // Layout implementation
};
```

---

## 🔄 State Management Strategy

### Server State (React Query)
```tsx
// API hooks using React Query
export function useFileUpload() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.post('/files/upload', formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['files']);
    },
  });
}

// Data fetching
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.get('/health'),
    refetchInterval: 30000, // 30 seconds
  });
}
```

### Local State (React Hooks)
```tsx
// Component-level state
const [activeTab, setActiveTab] = useState<'upload' | 'data' | 'chat'>('upload');
const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

// Custom hooks for complex state logic
export function useFileSelection() {
  const [files, setFiles] = useState<File[]>([]);
  
  const addFiles = useCallback((newFiles: File[]) => {
    setFiles(prev => [...prev, ...newFiles]);
  }, []);
  
  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);
  
  return { files, addFiles, removeFile };
}
```

### Global State (Context)
```tsx
// Theme context
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextType | null>(null);

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

---

## 🌐 API Integration

### API Client Setup
```tsx
// lib/api-client.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Type-Safe API Calls
```tsx
// lib/schemas.ts using Zod
export const FileUploadResponseSchema = z.object({
  file: z.object({
    id: z.string(),
    name: z.string(),
    size: z.number(),
    type: z.string(),
  }),
  uploadId: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
});

export type FileUploadResponse = z.infer<typeof FileUploadResponseSchema>;

// Usage in hooks
export function useFileUpload() {
  return useMutation({
    mutationFn: async (file: File): Promise<FileUploadResponse> => {
      const response = await api.post('/files/upload', formData);
      return validateSchema(FileUploadResponseSchema, response.data);
    },
  });
}
```

---

## 🎨 Styling Architecture

### Tailwind Configuration
```tsx
// tailwind.config.ts
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.2s ease-out',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};
```

### CSS Variables for Theming
```css
/* globals.css */
:root {
  --color-primary: 59 130 246; /* Blue 500 */
  --color-secondary: 139 92 246; /* Purple 500 */
  --border-radius: 0.5rem;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.dark {
  --color-primary: 96 165 250; /* Blue 400 */
  --color-secondary: 167 139 250; /* Purple 400 */
}
```

### Component Styling Patterns
```tsx
// Utility-first with composition
const cardVariants = {
  default: 'bg-white dark:bg-gray-800 rounded-lg shadow-md',
  elevated: 'bg-white dark:bg-gray-800 rounded-lg shadow-lg hover:shadow-xl transition-shadow',
  glass: 'backdrop-blur-md bg-white/10 dark:bg-gray-800/10 rounded-lg border border-white/20',
};

export const Card: React.FC<CardProps> = ({ variant = 'default', children }) => {
  return (
    <div className={cn(cardVariants[variant], 'p-6')}>
      {children}
    </div>
  );
};
```

---

## 📱 Responsive Design

### Mobile-First Approach
```tsx
// Responsive component design
export const DataTable: React.FC<DataTableProps> = ({ data }) => {
  return (
    <div className="w-full">
      {/* Mobile: Card layout */}
      <div className="block lg:hidden space-y-4">
        {data.map(item => (
          <Card key={item.id}>
            <CardContent>
              {/* Mobile card content */}
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Desktop: Table layout */}
      <div className="hidden lg:block">
        <table className="w-full">
          {/* Table content */}
        </table>
      </div>
    </div>
  );
};
```

### Breakpoint Strategy
```tsx
// Custom hooks for responsive behavior
export function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState<'mobile' | 'tablet' | 'desktop'>('mobile');
  
  useEffect(() => {
    const checkBreakpoint = () => {
      if (window.innerWidth >= 1024) setBreakpoint('desktop');
      else if (window.innerWidth >= 768) setBreakpoint('tablet');
      else setBreakpoint('mobile');
    };
    
    checkBreakpoint();
    window.addEventListener('resize', checkBreakpoint);
    return () => window.removeEventListener('resize', checkBreakpoint);
  }, []);
  
  return breakpoint;
}
```

---

## 🚀 Performance Optimization

### Code Splitting
```tsx
// Route-based splitting
const DataVisualization = lazy(() => import('./components/DataVisualization'));
const AIChat = lazy(() => import('./components/AIChat'));

// Component-based splitting with Suspense
<Suspense fallback={<LoadingSkeleton />}>
  <DataVisualization data={data} />
</Suspense>
```

### Image Optimization
```tsx
// Next.js Image component
import Image from 'next/image';

<Image
  src="/hero-image.jpg"
  alt="Dashboard preview"
  width={800}
  height={600}
  priority={true}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### Bundle Analysis
```bash
# Package.json scripts
"analyze": "ANALYZE=true npm run build"
"lighthouse": "lhci autorun"
```

---

## 🔒 Security Considerations

### Input Sanitization
```tsx
// Zod schemas for validation
const FileUploadSchema = z.object({
  file: z.instanceof(File).refine(
    (file) => file.size <= 10 * 1024 * 1024, // 10MB
    'File size must be less than 10MB'
  ).refine(
    (file) => ['text/csv', 'application/json'].includes(file.type),
    'Only CSV and JSON files are allowed'
  ),
});
```

### Authentication Flow
```tsx
// Protected route wrapper
export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { data: user, isLoading } = useCurrentUser();
    
    if (isLoading) return <LoadingSpinner />;
    if (!user) return <LoginPrompt />;
    
    return <Component {...props} />;
  };
}
```

---

This frontend architecture provides a solid foundation for building scalable, maintainable, and performant React applications with Next.js.
