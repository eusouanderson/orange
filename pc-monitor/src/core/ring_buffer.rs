//! Buffer circular de tamanho fixo com zero alocação dinâmica durante o loop quente.

use serde::{Deserialize, Serialize};

/// Buffer circular com capacidade máxima pré-alocada.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RingBuffer<T> {
    buffer: Vec<T>,
    capacity: usize,
    head: usize,
    is_full: bool,
}

impl<T: Clone> RingBuffer<T> {
    /// Cria um novo buffer com a capacidade estrita especificada.
    pub fn new(capacity: usize) -> Self {
        assert!(capacity > 0, "A capacidade do RingBuffer deve ser maior que zero.");
        Self {
            buffer: Vec::with_capacity(capacity),
            capacity,
            head: 0,
            is_full: false,
        }
    }

    /// Insere um novo item no buffer sobrescrevendo o elemento mais antigo se cheio.
    pub fn push(&mut self, item: T) {
        if self.buffer.len() < self.capacity {
            self.buffer.push(item);
        } else {
            self.buffer[self.head] = item;
            self.head = (self.head + 1) % self.capacity;
            self.is_full = true;
        }
    }

    /// Quantidade de elementos atualmente presentes no buffer.
    pub fn len(&self) -> usize {
        self.buffer.len()
    }

    /// Indica se o buffer está vazio.
    pub fn is_empty(&self) -> bool {
        self.buffer.is_empty()
    }

    /// Capacidade máxima do buffer.
    pub fn capacity(&self) -> usize {
        self.capacity
    }

    /// Limpa todos os elementos do buffer.
    pub fn clear(&mut self) {
        self.buffer.clear();
        self.head = 0;
        self.is_full = false;
    }

    /// Retorna os elementos em ordem cronológica (do mais antigo para o mais recente).
    pub fn to_chronological_vec(&self) -> Vec<T> {
        if !self.is_full {
            return self.buffer.clone();
        }
        let mut result = Vec::with_capacity(self.capacity);
        result.extend_from_slice(&self.buffer[self.head..]);
        result.extend_from_slice(&self.buffer[..self.head]);
        result
    }

    /// Retorna uma referência ao valor mais recente inserido no buffer.
    pub fn latest(&self) -> Option<&T> {
        if self.buffer.is_empty() {
            None
        } else if !self.is_full {
            self.buffer.last()
        } else {
            let idx = if self.head == 0 {
                self.capacity - 1
            } else {
                self.head - 1
            };
            Some(&self.buffer[idx])
        }
    }
}

impl RingBuffer<f32> {
    /// Calcula a média aritmética dos valores presentes no buffer.
    pub fn average(&self) -> f32 {
        if self.buffer.is_empty() {
            return 0.0;
        }
        let sum: f32 = self.buffer.iter().sum();
        sum / self.buffer.len() as f32
    }

    /// Encontra o valor máximo registrado.
    pub fn max(&self) -> f32 {
        self.buffer.iter().copied().fold(f32::MIN, f32::max)
    }

    /// Encontra o valor mínimo registrado.
    pub fn min(&self) -> f32 {
        self.buffer.iter().copied().fold(f32::MAX, f32::min)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ring_buffer_push_and_overflow() {
        let mut rb = RingBuffer::new(3);
        assert_eq!(rb.len(), 0);

        rb.push(10);
        rb.push(20);
        assert_eq!(rb.to_chronological_vec(), vec![10, 20]);
        assert_eq!(rb.latest(), Some(&20));

        rb.push(30);
        assert_eq!(rb.to_chronological_vec(), vec![10, 20, 30]);

        // Overflow: 10 deve ser substituído por 40
        rb.push(40);
        assert_eq!(rb.to_chronological_vec(), vec![20, 30, 40]);
        assert_eq!(rb.latest(), Some(&40));

        // Overflow: 20 deve ser substituído por 50
        rb.push(50);
        assert_eq!(rb.to_chronological_vec(), vec![30, 40, 50]);
        assert_eq!(rb.latest(), Some(&50));
    }

    #[test]
    fn test_ring_buffer_stats() {
        let mut rb = RingBuffer::new(5);
        rb.push(10.0);
        rb.push(20.0);
        rb.push(30.0);

        assert_eq!(rb.average(), 20.0);
        assert_eq!(rb.min(), 10.0);
        assert_eq!(rb.max(), 30.0);
    }
}
