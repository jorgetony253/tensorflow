# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Benchmarks for `tf.data.Dataset.from_tensor_slices()`."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.data.benchmarks import benchmark_base
from tensorflow.python.data.experimental.ops import get_single_element
from tensorflow.python.data.ops import dataset_ops
from tensorflow.python.framework import sparse_tensor


# TODO(b/119837791): Add eager benchmarks.
class FromTensorSlicesBenchmark(benchmark_base.DatasetBenchmarkBase):
  """Benchmarks for `tf.data.Dataset.from_tensor_slices()`."""

  def benchmark_slice_repeat_batch(self):
    input_size = 10000
    batch_size = 100
    num_epochs = 100
    num_elements = input_size * num_epochs // batch_size

    input_data = np.random.randn(input_size)

    dataset = (
        dataset_ops.Dataset.from_tensor_slices(input_data).repeat(
            num_epochs).batch(batch_size))

    self.run_and_report_benchmark(
        dataset,
        num_elements=num_elements,
        name="slice_repeat_batch_input_%d_batch_%d" % (input_size, batch_size))

  def benchmark_reshape_slice_repeat(self):
    input_size = 10000
    reshape_dim = [100, 100]
    num_epochs = 100

    num_elements = num_epochs * reshape_dim[0]

    input_data = np.random.randn(input_size)

    dataset = (
        dataset_ops.Dataset.from_tensor_slices(
            input_data.reshape(*reshape_dim)).repeat(num_epochs))

    self.run_and_report_benchmark(
        dataset,
        num_elements=num_elements,
        name="reshape_slice_repeat_input_%d" % input_size,
    )

  def benchmark_slice_repeat_sparse(self):
    non_zeros_per_row_values = [0, 1, 5, 10, 100]
    num_rows_values = [32, 64, 128, 1024]

    for non_zeros_per_row in non_zeros_per_row_values:
      tensor = sparse_tensor.SparseTensor(
          indices=np.arange(non_zeros_per_row, dtype=np.int64)[:, np.newaxis],
          values=np.arange(non_zeros_per_row, dtype=np.int64),
          dense_shape=[1000])

      for num_rows in num_rows_values:
        batched = dataset_ops.Dataset.from_tensors(
            tensor).repeat(num_rows).batch(num_rows)
        batched_tensor = get_single_element.get_single_element(batched)

        dataset = dataset_ops.Dataset.from_tensors(batched_tensor).flat_map(
            dataset_ops.Dataset.from_tensor_slices).repeat()
        self.run_and_report_benchmark(
            dataset,
            num_elements=100000,
            iters=5,
            name="slice_repeat_sparse_elements_per_row_%d_num_rows_%d" % (
                non_zeros_per_row, num_rows))

  def benchmark_slice_batch_cache_repeat(self):
    input_size = 10000
    batch_size = 100
    num_epochs = 100
    num_elements = input_size * num_epochs // batch_size

    input_data = np.random.randn(input_size)

    dataset = (
        dataset_ops.Dataset.from_tensor_slices(input_data).batch(
            batch_size).cache().repeat(num_epochs))

    self.run_and_report_benchmark(
        dataset,
        num_elements=num_elements,
        name="slice_batch_cache_repeat_input_%d_batch_%d" % (input_size,
                                                             batch_size))


if __name__ == "__main__":
  benchmark_base.test.main()
