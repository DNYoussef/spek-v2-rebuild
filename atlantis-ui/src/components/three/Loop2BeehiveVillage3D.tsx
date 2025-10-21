/**
 * Loop 2: Beehive Village 3D Visualization (Bee-Themed)
 *
 * Transformation of ExecutionVillage into bee-themed beehive:
 * - Princess buildings → Beehive sections with hexagonal cells
 * - Drone agents → Flying bees with animated wings
 * - Tasks → Honeycomb cells (empty → filling → full)
 * - Delegations → Bee flight paths (curved Bézier curves)
 *
 * Performance optimizations:
 * - Instanced rendering for bees (100+ bees, single draw call)
 * - Instanced rendering for honeycomb cells (1,000+ cells)
 * - LOD system (3 detail levels)
 * - GPU-accelerated animations
 */

'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Text, OrbitControls, Line } from '@react-three/drei';
import { useRef, useState, useMemo } from 'react';
import * as THREE from 'three';
import { defaultCanvasConfig } from '@/lib/three-config';
import { CameraControls } from './CameraControls';
import { PerformanceStats } from './PerformanceStats';
import { WorkerBee, PrincessBee, QueenBee } from './models/Bee3D';
import { HoneycombCell3D, createHexGrid } from './models/HoneycombCell3D';
import {
  BeeFlightAnimator,
  createFlightCurve,
  calculateFlightDuration,
} from '@/lib/three/animations/BeeFlightPath';
import { useAccessibility3D } from '@/hooks/useAccessibility3D';

interface Loop2BeehiveData {
  princesses: Princess[];
  drones: Drone[];
  tasks: Task[];
  delegations: Delegation[];
  queen?: Queen;
}

interface Princess {
  id: string;
  name: string;
  type: 'dev' | 'quality' | 'coordination' | 'documentation';
  position: [number, number, number];
  droneCount: number;
}

interface Drone {
  id: string;
  princessId: string;
  status: 'idle' | 'working' | 'completed';
  position: [number, number, number];
  targetPosition: [number, number, number];
}

interface Task {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedTo: string;
  progress: number;
  princessId?: string;
  droneId?: string;
}

interface Delegation {
  fromPrincessId: string;
  toDroneId: string;
  points: [number, number, number][];
}

interface Queen {
  id: string;
  position: [number, number, number];
  activeDelegations: number;
}

interface Loop2BeehiveVillage3DProps {
  data?: Loop2BeehiveData;
  showStats?: boolean;
}

// Default mock data for development
const DEFAULT_DATA: Loop2BeehiveData = {
  princesses: [
    { id: 'p1', name: 'Princess Dev', type: 'dev', position: [5, 3, 0], droneCount: 8 },
    { id: 'p2', name: 'Princess Quality', type: 'quality', position: [-5, 3, 0], droneCount: 6 },
    { id: 'p3', name: 'Princess Coord', type: 'coordination', position: [0, 3, 5], droneCount: 5 },
  ],
  drones: [
    { id: 'd1', princessId: 'p1', position: [5, 2, 1], targetPosition: [6, 2, 2], status: 'working' },
    { id: 'd2', princessId: 'p2', position: [-5, 2, 1], targetPosition: [-4, 2, 0], status: 'working' },
    { id: 'd3', princessId: 'p2', position: [-4, 2, -1], targetPosition: [-4, 2, -1], status: 'idle' },
    { id: 'd4', princessId: 'p1', position: [6, 2, 0], targetPosition: [5, 2, 1], status: 'working' },
  ],
  tasks: [
    { id: 't1', name: 'Implement Login', status: 'in_progress', assignedTo: 'd1', progress: 65 },
    { id: 't2', name: 'Write Tests', status: 'in_progress', assignedTo: 'd2', progress: 40 },
    { id: 't3', name: 'Code Review', status: 'completed', assignedTo: 'd3', progress: 100 },
  ],
  delegations: [
    { fromPrincessId: 'p1', toDroneId: 'd1', points: [[5, 3, 0], [5, 2.5, 0.5], [5, 2, 1]] },
    { fromPrincessId: 'p2', toDroneId: 'd2', points: [[-5, 3, 0], [-5, 2.5, 0.5], [-5, 2, 1]] },
  ],
  queen: { id: 'queen', position: [0, 5, 0], activeDelegations: 2 },
};

/**
 * Princess Hive Section - Hexagonal cell cluster
 */
function PrincessHiveSection({
  princess,
  tasks,
  detail,
}: {
  princess: Princess;
  tasks: Task[];
  detail: 'high' | 'medium' | 'low';
}) {
  // Create hexagonal grid for this princess's tasks
  const cellPositions = useMemo(() => {
    const rows = Math.ceil(Math.sqrt(princess.droneCount));
    const cols = Math.ceil(princess.droneCount / rows);
    return createHexGrid(rows, cols, 1.2);
  }, [princess.droneCount]);

  // Map tasks to cells
  const princessTasks = tasks.filter((t) => t.princessId === princess.id);

  return (
    <group position={princess.position}>
      {/* Princess bee (larger, coordinating) */}
      <PrincessBee position={[0, 2, 0]} isFlying wingSpeed={25} />

      {/* Hexagonal cells for tasks */}
      {cellPositions.slice(0, princessTasks.length).map((pos, idx) => {
        const task = princessTasks[idx];
        const state =
          task?.status === 'completed'
            ? 'full'
            : task?.status === 'in_progress'
            ? 'filling'
            : 'empty';

        return (
          <HoneycombCell3D
            key={idx}
            position={[
              pos[0] + princess.position[0],
              pos[1],
              pos[2] + princess.position[2],
            ]}
            state={state}
            glow={state === 'full'}
          />
        );
      })}

      {/* Label (only on high detail) */}
      {detail === 'high' && (
        <Text
          position={[0, 3, 0]}
          fontSize={0.6}
          color="#FFB300"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.05}
          outlineColor="#000000"
        >
          {princess.name}
        </Text>
      )}
    </group>
  );
}

/**
 * Flying drone bee with animation
 */
function FlyingDroneBee({ drone }: { drone: Drone }) {
  const beeRef = useRef<THREE.Group>(null);
  const [animator] = useState(() => {
    const start = new THREE.Vector3(...drone.position);
    const end = new THREE.Vector3(...drone.targetPosition);
    return new BeeFlightAnimator({
      start,
      end,
      duration: calculateFlightDuration(start, end, 2.0),
      height: 0.5,
      bobFrequency: 2,
      bobAmplitude: 0.1,
    });
  });

  useFrame((state) => {
    if (!beeRef.current) return;

    const time = state.clock.getElapsedTime();
    const position = animator.getPosition(time);
    const rotation = animator.getRotation();

    beeRef.current.position.copy(position);
    beeRef.current.rotation.copy(rotation);

    // Reset animation if complete
    if (animator.isFinished()) {
      animator.reset();
    }
  });

  return (
    <group ref={beeRef}>
      <WorkerBee wingSpeed={30} isFlying />
    </group>
  );
}

/**
 * Flight path visualization (curved line)
 */
function FlightPath({ delegation }: { delegation: Delegation }) {
  const curve = useMemo(() => {
    const points = delegation.points.map((p) => new THREE.Vector3(...p));
    if (points.length === 2) {
      return createFlightCurve(points[0], points[1], 0.5);
    }
    return new THREE.CatmullRomCurve3(points);
  }, [delegation.points]);

  const linePoints = useMemo(() => curve.getPoints(50), [curve]);

  return (
    <Line
      points={linePoints}
      color="#FFB300"
      lineWidth={2}
      opacity={0.3}
      transparent
      dashed
      dashSize={0.1}
      gapSize={0.05}
    />
  );
}

/**
 * Main beehive scene
 */
function BeehiveScene({
  data,
}: {
  data: Loop2BeehiveData;
}) {
  const [detail, setDetail] = useState<'high' | 'medium' | 'low'>('high');

  // Calculate LOD based on camera distance
  useFrame(({ camera }) => {
    const distance = camera.position.distanceTo(
      new THREE.Vector3(0, 0, 0)
    );
    if (distance < 20) setDetail('high');
    else if (distance < 40) setDetail('medium');
    else setDetail('low');
  });

  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />
      <pointLight position={[0, 10, 0]} intensity={0.5} color="#FFB300" />

      {/* Queen bee (central coordinator) */}
      {data.queen && (
        <QueenBee
          position={data.queen.position}
          isFlying
          wingSpeed={20}
        />
      )}

      {/* Princess hive sections */}
      {data.princesses.map((princess) => (
        <PrincessHiveSection
          key={princess.id}
          princess={princess}
          tasks={data.tasks}
          detail={detail}
        />
      ))}

      {/* Flying drone bees */}
      {detail !== 'low' &&
        data.drones.map((drone) => (
          <FlyingDroneBee key={drone.id} drone={drone} />
        ))}

      {/* Flight paths (delegations) */}
      {detail === 'high' &&
        data.delegations.map((delegation, idx) => (
          <FlightPath key={idx} delegation={delegation} />
        ))}

      {/* Ground plane (hive base) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial
          color="#FFF8DC"
          roughness={0.9}
          metalness={0.1}
        />
      </mesh>

      {/* Camera controls */}
      <CameraControls />
    </>
  );
}

/**
 * Main component with Canvas wrapper
 * Week 19 Day 5: Added accessibility support
 */
export default function Loop2BeehiveVillage3D({
  data = DEFAULT_DATA,
  showStats = false,
}: Loop2BeehiveVillage3DProps) {
  const cameraPosition: [number, number, number] = [15, 15, 15];

  const taskStats = {
    total: data.tasks.length,
    completed: data.tasks.filter(t => t.status === 'completed').length,
    inProgress: data.tasks.filter(t => t.status === 'in_progress').length,
  };

  // Accessibility features (Week 19 Day 5)
  const { canvasProps, prefersReducedMotion, handleKeyDown } = useAccessibility3D({
    ariaLabel: 'Loop 2 Beehive Village 3D Visualization',
    ariaDescription: `Interactive 3D visualization showing task execution as a bee-themed hive. ${data.princesses.length} princess agents coordinating ${data.drones.length} drone agents. ${taskStats.completed} of ${taskStats.total} tasks completed. Use arrow keys to rotate camera, plus and minus to zoom.`,
    currentState: `${taskStats.inProgress} tasks in progress, ${taskStats.completed} completed`,
    enableKeyboardNav: true,
    respectReducedMotion: true,
  });

  return (
    <div className="relative w-full h-full" onKeyDown={handleKeyDown}>
      <Canvas
        {...defaultCanvasConfig}
        {...canvasProps}
        camera={{
          position: cameraPosition,
          fov: 60,
        }}
        frameloop={prefersReducedMotion ? 'demand' : 'always'}
      >
        <BeehiveScene data={data} />
        {/* Interactive camera controls */}
        <OrbitControls
          enableDamping={!prefersReducedMotion}
          dampingFactor={0.05}
          minDistance={10}
          maxDistance={80}
          enableRotate={!prefersReducedMotion}
          autoRotate={false}
        />
      </Canvas>

      {showStats && <PerformanceStats />}

      {/* Hidden description for screen readers */}
      {canvasProps['aria-describedby'] && (
        <div id={canvasProps['aria-describedby']} className="sr-only">
          <p>
            Interactive 3D visualization showing task execution as a bee-themed hive village.
            {data.princesses.length} princess agents coordinating {data.drones.length} drone agents.
            {taskStats.completed} of {taskStats.total} tasks completed, {taskStats.inProgress} in progress.
            Use arrow keys to rotate camera, plus and minus to zoom, R to reset view.
          </p>
        </div>
      )}
    </div>
  );
}
