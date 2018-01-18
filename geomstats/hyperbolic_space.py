"""
Computations on the Hyperbolic space H_n
as embedded in Minkowski space R^{1,n}.

Elements of the Hyperbolic space are the elements
of Minkowski space of squared norm -1.

NB: we use "riemannian" to refer to "pseudo-riemannian".
"""

import math
import numpy as np

import RiemannianManifold

EPSILON = 1e-6
TOLERANCE = 1e-12

SINH_TAYLOR_COEFFS = [0., 1.,
                      0., 1 / math.factorial(3),
                      0., 1 / math.factorial(5),
                      0., 1 / math.factorial(7),
                      0., 1 / math.factorial(9)]
COSH_TAYLOR_COEFFS = [1., 0.,
                      1 / math.factorial(2), 0.,
                      1 / math.factorial(4), 0.,
                      1 / math.factorial(6), 0.,
                      1 / math.factorial(8), 0.]
INV_SINH_TAYLOR_COEFFS = [0., - 1. / 6.,
                          0., + 7. / 360.,
                          0., - 31. / 15120.,
                          0., + 127. / 604800.]
INV_TANH_TAYLOR_COEFFS = [0., + 1. / 3.,
                          0., - 1. / 45.,
                          0., + 2. / 945.,
                          0., -1. / 4725.]


def embedding_inner_product(vector_a, vector_b):
    """Minkowski inner product."""
    return np.dot(vector_a, vector_b) - 2 * vector_a[0] * vector_b[0]


def embedding_squared_norm(vector):
    """Minkowski norm."""
    return embedding_inner_product(vector, vector)


class HyperbolicSpace(RiemannianManifold):

    def belongs(self, point, tolerance=TOLERANCE):
        """
        By definition, points on the Hyperbolic space
        are points of Minkowski norm -1.
        Note: point must be given in extrinsic coordinates.
        """
        assert abs(embedding_squared_norm(point) + 1) < tolerance

    def intrinsic_to_extrinsic_coords(self, point_intrinsic):
        """
        From the intrinsic coordinates in the hyperbolic space,
        to the extrinsic coordinates in Minkowski space.
        """
        dimension = len(point_intrinsic)
        point_extrinsic = np.zeros(dimension + 1, 'float')
        point_extrinsic[1: dimension + 1] = point_intrinsic[0: dimension]
        point_extrinsic[0] = np.sqrt(1. + np.dot(point_intrinsic,
                                                 point_intrinsic))
        return point_extrinsic

    def extrinsic_to_intrinsic_coords(self, point_extrinsic):
        """
        From the extrinsic coordinates in Minkowski space,
        to the extrinsic coordinates in Hyperbolic space.
        """
        assert self.belongs(point_extrinsic)

        return point_extrinsic[1:]

    def projection_to_tangent_space(self, ref_point, vector):
        """
         Project the vector vector onto the tangent space at ref_point
         T_{ref_point}H = { w s.t. embedding_inner_product(ref_point, w) = 0 }
        """
        assert self.belongs(ref_point)

        inner_prod = embedding_inner_product(ref_point, vector)
        sq_norm_ref_point = embedding_squared_norm(ref_point)

        tangent_vec = vector - inner_prod * ref_point / sq_norm_ref_point
        return tangent_vec

    def riemannian_exp(self, ref_point, vector, epsilon=EPSILON):
        """
        Compute the Riemannian exponential at point ref_point
        of tangent vector tangent_vec wrt the metric obtained by
        embedding of the hyperbolic space in the minkowski space.

        This gives a point on the hyperbolic space.

        :param ref_point: a point on the hyperbolic space
        :param vector: vector
        :returns riem_exp: a point on the hyperbolic space
        """
        assert self.belongs(ref_point)

        tangent_vec = self.projection_to_tangent_space(ref_point, vector)
        norm_tangent_vec = math.sqrt(embedding_squared_norm(tangent_vec))

        if norm_tangent_vec < epsilon:
            coef_1 = (1. + COSH_TAYLOR_COEFFS[2] * norm_tangent_vec ** 2
                      + COSH_TAYLOR_COEFFS[4] * norm_tangent_vec ** 4
                      + COSH_TAYLOR_COEFFS[6] * norm_tangent_vec ** 6
                      + COSH_TAYLOR_COEFFS[8] * norm_tangent_vec ** 8)
            coef_2 = (1. + SINH_TAYLOR_COEFFS[3] * norm_tangent_vec ** 2
                      + SINH_TAYLOR_COEFFS[5] * norm_tangent_vec ** 4
                      + SINH_TAYLOR_COEFFS[7] * norm_tangent_vec ** 6
                      + SINH_TAYLOR_COEFFS[9] * norm_tangent_vec ** 8)
        else:
            coef_1 = np.cosh(norm_tangent_vec)
            coef_2 = np.sinh(norm_tangent_vec) / norm_tangent_vec

        riem_exp = coef_1 * ref_point + coef_2 * tangent_vec

        return riem_exp

    def riemannian_log(self, ref_point, point, epsilon=EPSILON):
        """
        Compute the Riemannian logarithm at point ref_point,
        of point wrt the metric obtained by
        embedding of the hyperbolic space in the minkowski space.

        This gives a tangent vector at point ref_point.

        :param ref_point: point on the hyperbolic space
        :param point: point on the hyperbolic space
        :returns riem_log: tangent vector at ref_point
        """
        assert self.belongs(ref_point)
        assert self.belongs(point)

        angle = self.riemannian_dist(ref_point, point)
        if angle < epsilon:
            coef_1 = (1. + INV_SINH_TAYLOR_COEFFS[1] * angle ** 2
                      + INV_SINH_TAYLOR_COEFFS[3] * angle ** 4
                      + INV_SINH_TAYLOR_COEFFS[5] * angle ** 6
                      + INV_SINH_TAYLOR_COEFFS[7] * angle ** 8)
            coef_2 = (1. + INV_TANH_TAYLOR_COEFFS[1] * angle ** 2
                      + INV_TANH_TAYLOR_COEFFS[3] * angle ** 4
                      + INV_TANH_TAYLOR_COEFFS[5] * angle ** 6
                      + INV_TANH_TAYLOR_COEFFS[7] * angle ** 8)
        else:
            coef_1 = angle / np.sinh(angle)
            coef_2 = angle / np.tanh(angle)
        return coef_1 * point - coef_2 * ref_point

    def riemannian_dist(self, point_a, point_b):
        """
        Compute the Riemannian logarithm at point ref_point,
        of point wrt the metric obtained by
        embedding of the hyperbolic space in the minkowski space.
        """
        assert self.belongs(point_a)
        assert self.belongs(point_b)

        sq_norm_a = embedding_squared_norm(point_a)
        sq_norm_b = embedding_squared_norm(point_b)
        inner_prod = embedding_inner_product(point_a, point_b)

        cosh_angle = - inner_prod / math.sqrt(sq_norm_a * sq_norm_b)

        if cosh_angle <= 1.:
            return 0.

        return np.arccosh(cosh_angle)

    def random_uniform(self, dimension, max_norm):
        """
        Generate a random element on the hyperbolic space.
        """
        point_intrinsic = (np.random.random_sample(dimension) - .5) * max_norm
        return self.intrinsic_to_extrinsic_coords(point_intrinsic)
