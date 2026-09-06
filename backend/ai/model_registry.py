"""RoboLab's 48-specialist model registry.

Each role is a model *slot*: deployments may point different roles at different
providers/models through environment variables, while local/beta deployments
can safely reuse one configured model. The registry keeps the orchestration
contract stable as the model fleet changes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRole:
    id: str
    name: str
    domain: str
    focus: str
    priority: int
    temperature: float = 0.15


_ROLES = [
    ("architect", "System Architect", "architecture", "Turn the natural-language goal into a coherent system architecture."),
    ("requirements", "Requirements Analyst", "planning", "Extract explicit requirements, constraints, assumptions, and acceptance criteria."),
    ("specification", "Technical Spec Writer", "planning", "Convert the goal into precise engineering specifications and interfaces."),
    ("feasibility", "Feasibility Engineer", "planning", "Identify technical feasibility, missing information, and practical alternatives."),
    ("bom", "BOM Engineer", "hardware", "Select and normalize components and produce a complete bill of materials."),
    ("component", "Component Specialist", "hardware", "Check component suitability, ratings, interfaces, and compatibility."),
    ("sensor", "Sensor Engineer", "hardware", "Design sensor selection, wiring, calibration, filtering, and data handling."),
    ("actuator", "Actuator Engineer", "hardware", "Design motors, servos, steppers, drivers, and actuator control safely."),
    ("power", "Power Systems Engineer", "electrical", "Analyze voltage rails, current demand, grounding, regulators, batteries, and protection."),
    ("digital", "Digital Electronics Engineer", "electrical", "Review GPIO, logic levels, pullups, buses, and digital interfaces."),
    ("analog", "Analog Electronics Engineer", "electrical", "Review ADC/DAC paths, analog conditioning, references, and noise."),
    ("embedded", "Embedded Systems Engineer", "firmware", "Define MCU architecture, timing, peripherals, interrupts, and firmware structure."),
    ("arduino", "Arduino Specialist", "firmware", "Produce board-appropriate Arduino C/C++ implementations and pin handling."),
    ("esp32", "ESP32 Specialist", "firmware", "Handle ESP32 peripherals, Wi-Fi/BLE, tasks, memory, and power-aware firmware."),
    ("stm32", "STM32 Specialist", "firmware", "Handle STM32 peripherals, HAL/LL patterns, timers, DMA, and embedded constraints."),
    ("raspberry_pi", "Raspberry Pi Specialist", "embedded", "Design Linux-side robotics control, GPIO, services, and Python/C++ integration."),
    ("micropython", "MicroPython Specialist", "firmware", "Design concise MicroPython implementations for supported boards."),
    ("cpp", "C/C++ Engineer", "firmware", "Review generated embedded C/C++ for correctness, lifetime, types, and portability."),
    ("python", "Python Engineer", "software", "Design robust Python tooling, robotics nodes, services, and automation."),
    ("flutter", "Flutter Engineer", "android", "Design reliable Android/Flutter integration for RoboLab project workflows."),
    ("api", "API Engineer", "software", "Validate REST/JSON contracts, errors, timeouts, retries, and compatibility."),
    ("robotics", "Robotics Engineer", "robotics", "Review robot-level behavior, kinematics assumptions, control flow, and integration."),
    ("control", "Control Systems Engineer", "robotics", "Design stable control logic, feedback loops, PID considerations, and limits."),
    ("motion", "Motion Planning Engineer", "robotics", "Reason about motion sequences, constraints, collision avoidance, and actuation."),
    ("navigation", "Navigation Engineer", "robotics", "Review localization, path planning, obstacle handling, and navigation logic."),
    ("computer_vision", "Computer Vision Engineer", "ai_robotics", "Design camera pipelines, detection logic, and vision-to-action interfaces."),
    ("ml", "ML Engineer", "ai_robotics", "Select appropriate ML approaches and define training/inference boundaries."),
    ("nlp", "Natural Language Engineer", "ai", "Translate natural-language project requests into structured engineering intent."),
    ("cad", "CAD Engineer", "mechanical", "Create mechanical design requirements, dimensions, interfaces, and fabrication constraints."),
    ("mechanical", "Mechanical Engineer", "mechanical", "Review structure, fasteners, loads, clearances, motion, and manufacturability."),
    ("materials", "Materials Engineer", "mechanical", "Evaluate material suitability, durability, heat, and environmental constraints."),
    ("thermal", "Thermal Engineer", "mechanical", "Check heat generation, dissipation, operating limits, and thermal risks."),
    ("simulation", "Simulation Engineer", "simulation", "Build a simulation-ready representation and identify variables and test cases."),
    ("circuit", "Circuit Designer", "electrical", "Turn architecture into a consistent circuit-level connection plan."),
    ("pcb", "PCB Engineer", "electrical", "Review PCB-level layout implications, grounding, decoupling, traces, and connectors."),
    ("protocols", "Protocol Engineer", "communications", "Review I2C, SPI, UART, CAN, USB, BLE, Wi-Fi, and application protocols."),
    ("wireless", "Wireless Engineer", "communications", "Design wireless links, reliability, range assumptions, and failure handling."),
    ("security", "Embedded Security Engineer", "security", "Review secrets, update paths, device trust, input validation, and attack surface."),
    ("reliability", "Reliability Engineer", "quality", "Identify single points of failure, degradation modes, and recovery behavior."),
    ("test", "Test Engineer", "quality", "Create unit, integration, simulation, and hardware-test cases with expected results."),
    ("compiler", "Build/Compiler Engineer", "quality", "Check build configuration, dependencies, toolchains, and compile-time failure risks."),
    ("debugger", "Debugging Engineer", "quality", "Find likely faults, rank hypotheses, and propose deterministic diagnostics."),
    ("verifier", "Independent Verifier", "quality", "Independently challenge the proposed design and detect contradictions."),
    ("auditor", "Engineering Auditor", "quality", "Audit the full output against requirements, safety, consistency, and evidence."),
    ("integrator", "Systems Integrator", "integration", "Reconcile specialist findings into one internally consistent project."),
    ("consensus", "Consensus Judge", "integration", "Resolve disagreements using evidence, constraints, and weighted specialist findings."),
    ("final_reviewer", "Final Review Engineer", "quality", "Perform the final release gate and identify unresolved blockers."),
]

ROLES: tuple[ModelRole, ...] = tuple(
    ModelRole(id=role_id, name=name, domain=domain, focus=focus, priority=1 if domain in {"quality", "electrical", "power", "safety"} else 2)
    for role_id, name, domain, focus in _ROLES
)

assert len(ROLES) == 48

ROLE_BY_ID = {role.id: role for role in ROLES}


def model_env_key(role_id: str) -> str:
    """Return the optional per-role model environment variable name."""
    return f"ROBOLAB_MODEL_{role_id.upper()}"
