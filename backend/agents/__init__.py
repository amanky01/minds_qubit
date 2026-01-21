import importlib
import pkgutil
import os
from typing import Dict, List, Optional
from agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

# Agent registry
_agent_registry: Dict[str, BaseAgent] = {}


def _discover_agents() -> Dict[str, BaseAgent]:
    """Automatically discover and load all agent classes"""
    agents = {}
    agents_dir = os.path.dirname(__file__)
    
    # Get all Python files in the agents directory
    for module_name in os.listdir(agents_dir):
        if module_name.endswith('.py') and module_name not in ['__init__.py', 'base.py']:
            try:
                # Remove .py extension
                agent_module_name = module_name[:-3]
                # Import the module
                module = importlib.import_module(f'agents.{agent_module_name}')
                
                # Find all classes that inherit from BaseAgent
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseAgent) and 
                        attr != BaseAgent):
                        agent_instance = attr()
                        agents[agent_instance.id] = agent_instance
                        logger.info(f"Loaded agent: {agent_instance.name} (id: {agent_instance.id})")
            except Exception as e:
                logger.error(f"Error loading agent from {module_name}: {e}")
                continue
    
    return agents


def initialize_agents():
    """Initialize the agent registry"""
    global _agent_registry
    _agent_registry = _discover_agents()
    logger.info(f"Initialized {len(_agent_registry)} agents")


def get_agent(agent_id: str) -> Optional[BaseAgent]:
    """Get an agent by ID"""
    return _agent_registry.get(agent_id)


def get_all_agents() -> List[BaseAgent]:
    """Get all registered agents"""
    return list(_agent_registry.values())


def get_agents_by_category(category: str) -> List[BaseAgent]:
    """Get all agents in a specific category"""
    return [agent for agent in _agent_registry.values() if agent.category == category]


def get_all_categories() -> List[str]:
    """Get all unique categories"""
    categories = set(agent.category for agent in _agent_registry.values())
    return sorted(list(categories))


# Initialize agents on module import
initialize_agents()
