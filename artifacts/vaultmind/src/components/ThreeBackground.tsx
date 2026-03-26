import { useRef, useMemo, Component, type ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function isWebGLAvailable(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      canvas.getContext('webgl2') ||
      canvas.getContext('webgl') ||
      canvas.getContext('experimental-webgl')
    );
  } catch {
    return false;
  }
}

function ParticleField() {
  const points = useRef<THREE.Points>(null);
  
  const particlesCount = 800;
  const positions = useMemo(() => {
    const pos = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.05;
      points.current.rotation.x = state.clock.elapsedTime * 0.025;
      const mouseX = (state.pointer.x * Math.PI) / 10;
      const mouseY = (state.pointer.y * Math.PI) / 10;
      points.current.rotation.x += (mouseY - points.current.rotation.x) * 0.05;
      points.current.rotation.y += (mouseX - points.current.rotation.y) * 0.05;
    }
  });

  return (
    <Points ref={points} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#00f5c8"
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

function WireframeMesh() {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.1;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.15;
    }
  });

  return (
    <mesh ref={meshRef} scale={3}>
      <icosahedronGeometry args={[1, 1]} />
      <meshBasicMaterial color="#0090ff" wireframe transparent opacity={0.15} />
    </mesh>
  );
}

class WebGLErrorBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

function CssFallbackBackground() {
  const particles = useMemo(() =>
    Array.from({ length: 80 }, (_, i) => ({
      id: i,
      width: Math.random() * 3 + 1,
      height: Math.random() * 3 + 1,
      left: Math.random() * 100,
      top: Math.random() * 100,
      color: i % 3 === 0 ? '#00f5c8' : i % 3 === 1 ? '#0090ff' : '#b537f2',
      opacity: Math.random() * 0.5 + 0.1,
      duration: Math.random() * 8 + 4,
      delay: Math.random() * 8,
    })),
    []
  );

  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden" style={{ background: '#020408' }}>
      <div className="absolute inset-0" style={{
        background: 'radial-gradient(ellipse at 20% 50%, rgba(0,245,200,0.07) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(0,144,255,0.07) 0%, transparent 60%), radial-gradient(ellipse at 60% 80%, rgba(181,55,242,0.05) 0%, transparent 60%)'
      }} />
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full"
          style={{
            width: p.width + 'px',
            height: p.height + 'px',
            left: p.left + '%',
            top: p.top + '%',
            background: p.color,
            opacity: p.opacity,
            boxShadow: `0 0 6px ${p.color}`,
            animation: `pulse ${p.duration}s ease-in-out infinite`,
            animationDelay: `-${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

export function ThreeBackground() {
  const webglAvailable = useMemo(() => isWebGLAvailable(), []);

  if (!webglAvailable) {
    return <CssFallbackBackground />;
  }

  return (
    <WebGLErrorBoundary fallback={<CssFallbackBackground />}>
      <div className="fixed inset-0 z-[-1] bg-background">
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse at center, rgba(0,245,200,0.03) 0%, transparent 70%)',
          mixBlendMode: 'screen'
        }} />
        <Canvas
          camera={{ position: [0, 0, 8], fov: 60 }}
          onCreated={({ gl }) => {
            gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          }}
        >
          <ParticleField />
          <WireframeMesh />
        </Canvas>
      </div>
    </WebGLErrorBoundary>
  );
}
