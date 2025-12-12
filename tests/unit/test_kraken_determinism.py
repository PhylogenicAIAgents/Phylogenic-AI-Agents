"""Deterministic tests for Kraken LNN with seeded RNG."""

import pytest
import numpy as np
from unittest.mock import patch

from allele.kraken_lnn import KrakenLNN, LiquidStateMachine
from allele import LiquidDynamics
from tests.test_utils import generate_test_sequence


class TestKrakenDeterminism:
    """Deterministic tests using seeded random number generators."""

    @pytest.fixture
    def deterministic_lsm(self):
        """Create LiquidStateMachine with seeded RNG."""
        with patch('numpy.random.seed'):
            lsm = LiquidStateMachine(reservoir_size=50, connectivity=0.1)
        # Manually seed for deterministic behavior
        np.random.seed(42)
        return lsm

    @pytest.fixture
    def deterministic_lnn(self):
        """Create KrakenLNN with seeded RNG."""
        with patch('numpy.random.seed'):
            lnn = KrakenLNN(reservoir_size=100, connectivity=0.1)
        # Seed for deterministic behavior
        np.random.seed(123)
        return lnn

    def test_lsm_deterministic_outputs_same_seed(self):
        """Test that LiquidStateMachine produces identical outputs with same seed."""
        # Create two LSMs with same seed
        np.random.seed(42)
        lsm1 = LiquidStateMachine(reservoir_size=50, connectivity=0.1)

        np.random.seed(42)
        lsm2 = LiquidStateMachine(reservoir_size=50, connectivity=0.1)

        # Process same sequence
        sequence = [0.5, 0.3, 0.8, 0.2, 0.9]

        outputs1 = lsm1.process_sequence(sequence)
        outputs2 = lsm2.process_sequence(sequence)

        # Outputs should be identical
        np.testing.assert_array_equal(outputs1, outputs2)

    def test_lsm_deterministic_outputs_different_seed(self):
        """Test that LiquidStateMachine produces different outputs with different seeds."""
        np.random.seed(42)
        lsm1 = LiquidStateMachine(reservoir_size=50, connectivity=0.1)

        np.random.seed(43)
        lsm2 = LiquidStateMachine(reservoir_size=50, connectivity=0.1)

        sequence = [0.5, 0.3, 0.8, 0.2, 0.9]

        outputs1 = lsm1.process_sequence(sequence)
        outputs2 = lsm2.process_sequence(sequence)

        # Outputs should be different (at least some differences)
        assert not np.array_equal(outputs1, outputs2)

    @pytest.mark.asyncio
    async def test_kraken_lnn_deterministic_processing(self, deterministic_lnn):
        """Test that KrakenLNN produces deterministic results with seeded RNG."""
        sequence = generate_test_sequence(20, seed=999)

        # Process same sequence twice
        result1 = await deterministic_lnn.process_sequence(sequence)
        result2 = await deterministic_lnn.process_sequence(sequence)

        # Results should be identical for deterministic processing
        assert result1['success'] == result2['success']
        np.testing.assert_array_equal(
            result1['liquid_outputs'],
            result2['liquid_outputs']
        )
        np.testing.assert_array_equal(
            result1['reservoir_state'],
            result2['reservoir_state']
        )

    @pytest.mark.asyncio
    async def test_kraken_lnn_deterministic_memory(self, deterministic_lnn):
        """Test that memory operations are deterministic."""
        sequences = [
            generate_test_sequence(10, seed=i) for i in range(5)
        ]

        # Process sequences and check memory state after each
        memory_states = []
        for seq in sequences:
            await deterministic_lnn.process_sequence(seq, memory_consolidation=False)
            memory_states.append(deterministic_lnn.temporal_memory.memories.copy())

        # Reset and process again
        deterministic_lnn.temporal_memory.memories.clear()
        np.random.seed(123)  # Reset seed

        for i, seq in enumerate(sequences):
            await deterministic_lnn.process_sequence(seq, memory_consolidation=False)
            # Memory should match previous run
            assert len(memory_states[i]) == len(deterministic_lnn.temporal_memory.memories)

    def test_lsm_reproducibility_across_initializations(self):
        """Test LSM reproducibility across multiple initializations with same seed."""
        sequence = [0.1, 0.5, 0.9, 0.2, 0.7]

        results = []
        for i in range(3):
            np.random.seed(100)
            lsm = LiquidStateMachine(reservoir_size=50, connectivity=0.1)
            output = lsm.process_sequence(sequence)
            results.append(output)

        # All results should be identical
        for i in range(1, len(results)):
            np.testing.assert_array_equal(results[0], results[i])

    def test_reservoir_state_deterministic_evolution(self):
        """Test that reservoir state evolves deterministically."""
        np.random.seed(200)
        lsm = LiquidStateMachine(reservoir_size=30, connectivity=0.15)

        # Record state evolution
        sequence = [0.3, 0.6, 0.9, 0.1]
        states = []

        for value in sequence:
            states.append(lsm.state.copy())
            lsm.process_input(value)

        # Reset and repeat
        np.random.seed(200)
        lsm2 = LiquidStateMachine(reservoir_size=30, connectivity=0.15)
        states2 = []

        for value in sequence:
            states2.append(lsm2.state.copy())
            lsm2.process_input(value)

        # States should match exactly
        for s1, s2 in zip(states, states2):
            np.testing.assert_array_equal(s1, s2)

    @pytest.mark.asyncio
    async def test_deterministic_sequence_chunking(self, deterministic_lnn):
        """Test deterministic processing of chunked sequences."""
        long_sequence = generate_test_sequence(50, seed=777)

        # Process in chunks
        chunk_size = 10
        chunk_results = []

        for i in range(0, len(long_sequence), chunk_size):
            chunk = long_sequence[i:i+chunk_size]
            result = await deterministic_lnn.process_sequence(chunk)
            chunk_results.append(result)

        # Process entire sequence
        full_result = await deterministic_lnn.process_sequence(long_sequence)

        # Results should be consistent (though not identical due to state evolution)
        assert full_result['success'] is True
        assert len(full_result['liquid_outputs']) == len(long_sequence)

    def test_adaptive_weights_deterministic_updates(self):
        """Test that adaptive weight updates are deterministic."""
        np.random.seed(300)
        lsm1 = LiquidStateMachine(reservoir_size=40, connectivity=0.1)

        np.random.seed(300)
        lsm2 = LiquidStateMachine(reservoir_size=40, connectivity=0.1)

        sequence = [0.4, 0.7, 0.2, 0.8, 0.5]

        # Process with learning enabled
        lsm1.process_sequence(sequence, learning_enabled=True)
        lsm2.process_sequence(sequence, learning_enabled=True)

        # Weights should be identical
        np.testing.assert_array_equal(
            lsm1.adaptive_weights.weights,
            lsm2.adaptive_weights.weights
        )

    def test_liquid_dynamics_deterministic_behavior(self):
        """Test that liquid dynamics produce deterministic results."""
        np.random.seed(400)
        dynamics1 = LiquidDynamics(viscosity=0.2, temperature=1.0, pressure=1.0)

        np.random.seed(400)
        dynamics2 = LiquidDynamics(viscosity=0.2, temperature=1.0, pressure=1.0)

        # Test perturbation calculation
        input_force = 0.5

        perturbation1 = dynamics1.calculate_perturbation(input_force, np.random.random(50))
        perturbation2 = dynamics2.calculate_perturbation(input_force, np.random.random(50))

        # Same initial seed should produce identical perturbations
        np.testing.assert_array_equal(perturbation1, perturbation2)

    def test_deterministic_memory_consolidation(self):
        """Test that memory consolidation is deterministic."""
        np.random.seed(500)

        lnn = KrakenLNN(reservoir_size=80, connectivity=0.05)
        lnn.temporal_memory.max_entries = 50

        # Fill memory with same sequences
        sequences = [generate_test_sequence(5, seed=i) for i in range(30)]

        import asyncio
        for seq in sequences:
            asyncio.run(lnn.process_sequence(seq, memory_consolidation=False))

        # Get memory state before consolidation
        pre_consolidation = lnn.temporal_memory.memories.copy()

        # Consolidate
        asyncio.run(lnn.process_sequence(generate_test_sequence(5), memory_consolidation=True))

        # Reset and repeat process
        np.random.seed(500)
        lnn2 = KrakenLNN(reservoir_size=80, connectivity=0.05)
        lnn2.temporal_memory.max_entries = 50

        for seq in sequences:
            asyncio.run(lnn2.process_sequence(seq, memory_consolidation=False))

        pre_consolidation2 = lnn2.temporal_memory.memories.copy()

        # Pre-consolidation states should match
        assert len(pre_consolidation) == len(pre_consolidation2)

        # Final consolidation
        asyncio.run(lnn2.process_sequence(generate_test_sequence(5), memory_consolidation=True))

        # Memory counts should match after consolidation
        assert len(lnn.temporal_memory.memories) == len(lnn2.temporal_memory.memories)

    def test_weight_initialization_determinism(self):
        """Test that weight initialization is deterministic."""
        weights1 = []
        weights2 = []

        # Same seed produces same weights
        np.random.seed(600)
        adaptive_weights1 = AdaptiveWeightMatrix(50, 50, seed=42)
        weights1.append(adaptive_weights1.weights.copy())

        np.random.seed(600)
        adaptive_weights2 = AdaptiveWeightMatrix(50, 50, seed=42)
        weights2.append(adaptive_weights2.weights.copy())

        np.testing.assert_array_equal(weights1[0], weights2[0])

        # Different seeds produce different weights
        np.random.seed(601)
        adaptive_weights3 = AdaptiveWeightMatrix(50, 50, seed=43)
        weights1.append(adaptive_weights3.weights.copy())

        # Should be different
        assert not np.array_equal(weights1[0], weights1[1])

    def test_noise_generation_determinism(self):
        """Test that noise generation is deterministic."""
        np.random.seed(700)
        lsm1 = LiquidStateMachine(reservoir_size=30)

        inputs = [0.2, 0.6, 0.8]
        noisy_outputs1 = []

        for inp in inputs:
            noisy_out = lsm1._add_liquid_noise(inp)
            noisy_outputs1.append(noisy_out)

        # Same seed should produce same noise
        np.random.seed(700)
        lsm2 = LiquidStateMachine(reservoir_size=30)

        noisy_outputs2 = []
        for inp in inputs:
            noisy_out = lsm2._add_liquid_noise(inp)
            noisy_outputs2.append(noisy_out)

        for out1, out2 in zip(noisy_outputs1, noisy_outputs2):
            assert out1 == out2  # Deterministic noise
