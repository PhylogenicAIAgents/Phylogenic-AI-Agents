"""Performance benchmarks for Kraken LNN scaling and sequence processing."""

import pytest
import time
import numpy as np
import asyncio
from typing import List, Dict, Any

from allele.kraken_lnn import KrakenLNN, LiquidStateMachine
from tests.test_utils import generate_test_sequence


class TestKrakenScalingBenchmarks:
    """Performance benchmarks for Kraken LNN scaling behavior."""

    @pytest.mark.benchmark
    def test_reservoir_scaling_performance(self, benchmark):
        """Benchmark reservoir size scaling performance."""
        def process_sequence_with_reservoir_size(size):
            lnn = KrakenLNN(reservoir_size=size, connectivity=0.1)
            sequence = generate_test_sequence(50)
            
            start_time = time.time()
            result = asyncio.run(lnn.process_sequence(sequence))
            processing_time = time.time() - start_time
            
            assert result['success'] is True
            return processing_time
        
        # Test different reservoir sizes
        sizes = [50, 100, 200]
        
        for size in sizes:
            processing_time = benchmark(process_sequence_with_reservoir_size, size)
            
            # Performance thresholds for GH runners
            if size <= 100:
                assert processing_time < 2.0  # 2 seconds max for smaller reservoirs
            else:
                assert processing_time < 5.0  # 5 seconds max for larger reservoirs

    @pytest.mark.benchmark
    def test_sequence_length_scaling(self, benchmark):
        """Benchmark processing time vs sequence length."""
        def process_sequence_of_length(length):
            lnn = KrakenLNN(reservoir_size=100, connectivity=0.1)
            sequence = generate_test_sequence(length)
            
            start_time = time.time()
            result = asyncio.run(lnn.process_sequence(sequence))
            processing_time = time.time() - start_time
            
            assert result['success'] is True
            return processing_time
        
        # Test different sequence lengths
        lengths = [10, 50, 100, 200]
        times = []
        
        for length in lengths:
            processing_time = benchmark(process_sequence_of_length, length)
            times.append(processing_time)
            
            # Should scale roughly linearly (not exponentially)
            if len(times) > 1:
                scaling_factor = times[-1] / times[0]
                length_factor = length / lengths[0]
                
                # Allow for some overhead but shouldn't be exponential
                assert scaling_factor < length_factor * 2

    @pytest.mark.benchmark
    def test_connectivity_impact_on_performance(self, benchmark):
        """Benchmark performance impact of different connectivity values."""
        def process_with_connectivity(connectivity):
            lnn = KrakenLNN(reservoir_size=100, connectivity=connectivity)
            sequence = generate_test_sequence(100)
            
            start_time = time.time()
            result = asyncio.run(lnn.process_sequence(sequence))
            processing_time = time.time() - start_time
            
            assert result['success'] is True
            return processing_time
        
        # Test different connectivity values
        connectivities = [0.05, 0.1, 0.2, 0.5]
        times = []
        
        for conn in connectivities:
            processing_time = benchmark(process_with_connectivity, conn)
            times.append(processing_time)
            
            # Higher connectivity should take longer (more connections to process)
            if len(times) > 1:
                # But shouldn't be dramatically different
                max_ratio = max(times) / min(times)
                assert max_ratio < 3.0  # No more than 3x difference

    @pytest.mark.benchmark
    def test_memory_consolidation_performance(self, benchmark):
        """Benchmark memory consolidation performance."""
        def benchmark_memory_consolidation():
            lnn = KrakenLNN(reservoir_size=100, connectivity=0.1)
            
            # Fill memory with multiple sequences
            sequences = [generate_test_sequence(20, seed=i) for i in range(50)]
            
            # First, add all memories
            for seq in sequences:
                asyncio.run(lnn.process_sequence(seq, memory_consolidation=False))
            
            initial_memory_count = len(lnn.temporal_memory.memories)
            
            # Benchmark consolidation
            start_time = time.time()
            consolidation_seq = generate_test_sequence(20)
            result = asyncio.run(lnn.process_sequence(consolidation_seq, memory_consolidation=True))
            consolidation_time = time.time() - start_time
            
            final_memory_count = len(lnn.temporal_memory.memories)
            
            assert result['success'] is True
            assert final_memory_count <= initial_memory_count
            
            return consolidation_time
        
        consolidation_time = benchmark(benchmark_memory_consolidation)
        
        # Memory consolidation should be relatively fast
        assert consolidation_time < 1.0  # 1 second max

    @pytest.mark.benchmark
    def test_liquid_state_machine_performance(self, benchmark):
        """Benchmark LiquidStateMachine individual operations."""
        def benchmark_lsm_operations():
            lsm = LiquidStateMachine(reservoir_size=100, connectivity=0.1)
            sequence = generate_test_sequence(100)
            
            start_time = time.time()
            outputs = lsm.process_sequence(sequence)
            processing_time = time.time() - start_time
            
            assert len(outputs) == len(sequence)
            assert all(np.isfinite(outputs))
            
            return processing_time
        
        processing_time = benchmark(benchmark_lsm_operations)
        
        # LSM operations should be fast
        assert processing_time < 0.5  # 500ms max

    @pytest.mark.benchmark
    def test_batch_sequence_processing(self, benchmark):
        """Benchmark processing multiple sequences in batch."""
        def benchmark_batch_processing():
            lnn = KrakenLNN(reservoir_size=100, connectivity=0.1)
            
            # Create batch of sequences
            sequences = [generate_test_sequence(50, seed=i) for i in range(10)]
            
            start_time = time.time()
            results = []
            
            for seq in sequences:
                result = asyncio.run(lnn.process_sequence(seq))
                results.append(result)
            
            total_time = time.time() - start_time
            
            # All results should be successful
            assert all(r['success'] for r in results)
            assert len(results) == len(sequences)
            
            return total_time
        
        batch_time = benchmark(benchmark_batch_processing)
        
        # Batch processing should be efficient
        assert batch_time < 10.0  # 10 seconds max for 10 sequences

    @pytest.mark.benchmark
    def test_large_reservoir_performance_limit(self, benchmark):
        """Test performance limits for large reservoirs to prevent OOM."""
        def process_large_reservoir():
            # Test with moderately large reservoir
            lnn = KrakenLNN(reservoir_size=500, connectivity=0.05)  # Lower connectivity for large size
            sequence = generate_test_sequence(100)
            
            start_time = time.time()
            result = asyncio.run(lnn.process_sequence(sequence))
            processing_time = time.time() - start_time
            
            assert result['success'] is True
            assert len(result['reservoir_state']) == 500
            
            return processing_time
        
        processing_time = benchmark(process_large_reservoir)
        
        # Large reservoir should still complete in reasonable time
        assert processing_time < 10.0  # 10 seconds max

    @pytest.mark.benchmark
    def test_memory_efficiency_under_load(self, benchmark):
        """Benchmark memory efficiency during continuous processing."""
        def benchmark_memory_efficiency():
            lnn = KrakenLNN(reservoir_size=200, connectivity=0.1)
            
            # Process many sequences to test memory efficiency
            start_time = time.time()
            
            for i in range(100):
                sequence = generate_test_sequence(25, seed=i)
                result = asyncio.run(lnn.process_sequence(sequence))
                
                if not result['success']:
                    break
            
            total_time = time.time() - start_time
            
            # Should complete all sequences without issues
            return total_time
        
        total_time = benchmark(benchmark_memory_efficiency)
        
        # Continuous processing should be stable
        avg_time_per_sequence = total_time / 100
        assert avg_time_per_sequence < 0.5  # Average < 500ms per sequence

    @pytest.mark.benchmark
    def test_initialization_performance(self, benchmark):
        """Benchmark initialization time for different configurations."""
        def initialize_lnn_with_size(size):
            start_time = time.time()
            lnn = KrakenLNN(reservoir_size=size, connectivity=0.1)
            init_time = time.time() - start_time
            
            assert lnn.reservoir_size == size
            assert lnn.liquid_reservoir is not None
            assert lnn.temporal_memory is not None
            
            return init_time
        
        # Test initialization time for different sizes
        sizes = [50, 100, 200, 500]
        init_times = []
        
        for size in sizes:
            init_time = benchmark(initialize_lnn_with_size, size)
            init_times.append(init_time)
            
            # Initialization should be relatively fast
            assert init_time < 2.0  # 2 seconds max
            
            # Larger sizes should take longer but not dramatically
            if len(init_times) > 1:
                scaling_ratio = init_times[-1] / init_times[0]
                size_ratio = size / sizes[0]
                assert scaling_ratio < size_ratio * 1.5

    @pytest.mark.benchmark
    async def test_concurrent_processing_performance(self, benchmark):
        """Benchmark concurrent processing capabilities."""
        async def benchmark_concurrent_processing():
            lnn = KrakenLNN(reservoir_size=100, connectivity=0.1)
            
            # Create multiple sequences
            sequences = [generate_test_sequence(50, seed=i) for i in range(5)]
            
            start_time = time.time()
            
            # Process sequences concurrently
            tasks = [lnn.process_sequence(seq) for seq in sequences]
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # All should complete successfully
            assert all(r['success'] for r in results)
            
            return total_time
        
        concurrent_time = benchmark.pedantic(benchmark_concurrent_processing, rounds=3)
        
        # Concurrent processing should be faster than sequential
        sequential_time = concurrent_time * 1.5  # Allow some overhead
        assert concurrent_time < sequential_time

    @pytest.mark.benchmark
    def test_dynamics_calculation_performance(self, benchmark):
        """Benchmark liquid dynamics calculation performance."""
        def benchmark_dynamics():
            from allele.kraken_lnn import LiquidDynamics
            
            dynamics = LiquidDynamics(viscosity=0.2, temperature=1.0, pressure=1.0)
            reservoir_state = np.random.random(100)  # Random state
            
            start_time = time.time()
            
            # Calculate dynamics for multiple time steps
            for _ in range(100):
                perturbation = dynamics.calculate_perturbation(0.5, reservoir_state)
                reservoir_state += perturbation * 0.1  # Simple update
            
            calculation_time = time.time() - start_time
            
            assert np.all(np.isfinite(reservoir_state))
            
            return calculation_time
        
        calc_time = benchmark(benchmark_dynamics)
        
        # Dynamics calculations should be fast
        assert calc_time < 0.1  # 100ms max for 100 calculations

    @pytest.mark.benchmark
    def test_weight_matrix_operations_performance(self, benchmark):
        """Benchmark weight matrix operations."""
        def benchmark_weight_operations():
            lsm = LiquidStateMachine(reservoir_size=150, connectivity=0.1)
            
            start_time = time.time()
            
            # Perform multiple weight updates
            for _ in range(50):
                lsm.adaptive_weights.update(np.random.random(150), learning_rate=0.01)
            
            operation_time = time.time() - start_time
            
            # Weight matrix should remain valid
            assert np.all(np.isfinite(lsm.adaptive_weights.weights))
            
            return operation_time
        
        op_time = benchmark(benchmark_weight_operations)
        
        # Weight operations should be efficient
        assert op_time < 1.0  # 1 second max for 50 updates
