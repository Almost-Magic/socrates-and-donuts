# Interaction Design Specifications

## Navigation

### Desktop
- **Left sidebar**: Persistent navigation icons + labels
- **Width**: 240px collapsed, 280px expanded
- **Active state**: Gold underline or background highlight
- **Transitions**: Slide + fade, 200ms ease

### Mobile
- **Bottom navigation bar**: 4-5 primary actions
- **Hamburger menu**: For full navigation drawer
- **Gesture**: Swipe right to open sidebar

### Crisis Access
- **Always visible**: Floating button or header icon
- **Position**: Bottom-right on desktop, top-right on mobile
- **Color**: Subtle but recognizable (not alarmist red)

## Components

### Buttons
- **Primary**: Gold background, midnight text, rounded-lg
- **Secondary**: Midnight-800 background, gold border, rounded-lg
- **Text-only**: Transparent background, gold text
- **Disabled**: 50% opacity, no pointer events

### Cards
- **Background**: Midnight-800 or midnight-800/50
- **Border**: 1px midnight-700
- **Radius**: 12px (lg) or 8px (md)
- **Hover**: Subtle lift, border color change

### Inputs
- **Background**: Midnight-900
- **Border**: 1px midnight-700
- **Focus**: Gold/50 border color, outline none
- **Radius**: 8px
- **Text**: Gray-200, 16px base

### Typography
- **Headings**: Gray-200, 24-32px, light weight
- **Body**: Gray-400, 16px, regular
- **Captions**: Gray-500, 14px
- **Gold accent**: For emphasis, hierarchy

## Animations

### Page Transitions
- **Enter**: Fade in + slide up, 300ms ease
- **Exit**: Fade out, 200ms ease
- **Stagger**: For lists, 50ms delay between items

### Micro-interactions
- **Button press**: Scale down 2%, 100ms
- **Hover**: Border color change, 200ms
- **Success feedback**: Green check pulse
- **Error feedback**: Red shake, 400ms

### Special Effects
- **Burn animation**: CSS particles, fading to transparent
- **Vault lock**: Rotate lock icon, 500ms
- **Weather transitions**: Smooth interpolation between states

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| xs | 0-639px | Single column, bottom nav |
| sm | 640-767px | Single column, full nav |
| md | 768-1023px | Two columns possible |
| lg | 1024-1279px | Full sidebar available |
| xl | 1280px+ | Multi-column layouts |

## Accessibility

### Keyboard Navigation
- **Tab**: Focus order follows visual hierarchy
- **Enter/Space**: Activate focused elements
- **Escape**: Close modals, cancel actions
- **Arrow keys**: Navigate lists, sliders

### Screen Readers
- **ARIA labels**: All interactive elements
- **Live regions**: For dynamic content updates
- **Focus management**: Proper focus trapping in modals

### Color Contrast
- **AA compliance**: Minimum 4.5:1 for body text
- **AAA preferred**: 7:1 for important text
- **Not color-only**: Icons paired with labels

### Motion Reduction
- **Respects `prefers-reduced-motion`**
- **Fallback**: Instant transitions, no animations
- **No auto-playing animations**: User must trigger

## Data Display

### Lists
- **Virtualization**: For lists >100 items
- **Pagination**: Or infinite scroll with manual trigger
- **Empty states**: Clear "nothing here" messaging

### Charts/Graphs
- **Emotional Weather Map**: Calendar view + trend line
- **Body Compass**: SVG body diagram with clickable zones
- **Vault Timeline**: Horizontal timeline of locked messages

### Empty States
- **Illustration**: Simple, friendly graphic
- **Guidance**: What to do next
- **Action**: Primary button to start

## Loading States

### Immediate
- **Skeleton screens**: Match final layout
- **Shimmer effect**: Left to right motion

### Longer Operations
- **Progress indicator**: Percentage or steps
- **Toast notification**: "Saving..." → "Saved"

### Error States
- **Graceful degradation**: What still works
- **Retry action**: Clear CTA
- **Error message**: Clear, actionable, not technical
