# -*- coding: utf-8 -*-
"""
Free Lie Algebras

AUTHORS:

- Travis Scrimshaw (2013-05-03): Initial version

REFERENCES:

- [Bou1989]_
- [Reu2003]_
"""

# ****************************************************************************
#       Copyright (C) 2013-2017 Travis Scrimshaw <tcscrims at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# *****************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.misc.bindable_class import BindableClass
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.indexed_generators import (IndexedGenerators,
                                               standardize_names_index_set)
from sage.categories.realizations import Realizations, Category_realization_of_parent
from sage.categories.lie_algebras import LieAlgebras
from sage.categories.homset import Hom

from sage.algebras.free_algebra import FreeAlgebra
from sage.algebras.lie_algebras.lie_algebra import FinitelyGeneratedLieAlgebra
from sage.algebras.lie_algebras.lie_algebra_element import (LieGenerator,
                                                            GradedLieBracket,
                                                            LyndonBracket,
                                                            FreeLieAlgebraElement)
from sage.algebras.lie_algebras.morphism import LieAlgebraHomomorphism_im_gens
from sage.misc.superseded import experimental_warning

from sage.rings.integer_ring import ZZ

class FreeLieBasis_abstract(FinitelyGeneratedLieAlgebra, IndexedGenerators, BindableClass):
    """
    Abstract base class for all bases of a free Lie algebra.
    """
    def __init__(self, lie, basis_name):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.Hall()
            doctest:warning
            ...
            FutureWarning: The Hall basis has not been fully proven correct, but currently no bugs are known
            See https://github.com/sagemath/sage/issues/16823 for details.
            Free Lie algebra generated by (x, y) over Rational Field in the Hall basis
        """
        self._basis_name = basis_name
        IndexedGenerators.__init__(self, lie._indices, prefix='', bracket=False)
        FinitelyGeneratedLieAlgebra.__init__(self, lie.base_ring(),
                            names=lie._names, index_set=lie._indices,
                            category=FreeLieAlgebraBases(lie))

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.Hall()
            Free Lie algebra generated by (x, y) over Rational Field in the Hall basis
            sage: L.Lyndon()
            Free Lie algebra generated by (x, y) over Rational Field in the Lyndon basis
        """
        return "{0} in the {1} basis".format(self.realization_of(), self._basis_name)

    def _repr_term(self, x):
        """
        Return a string representation for ``x``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x,y')
            sage: H = L.Hall()
            sage: x,y = H.gens()
            sage: H._repr_term(x.leading_support())
            'x'
            sage: a = H([x, y]).leading_support()
            sage: H._repr_term(a)
            '[x, y]'
        """
        return repr(x)

    def _latex_term(self, x):
        r"""
        Return a `\LaTeX` representation for ``x``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x,y')
            sage: H = L.Hall()
            sage: x,y = H.gens()
            sage: H._latex_term(x.leading_support())
            'x'
            sage: a = H([x, y]).leading_support()
            sage: H._latex_term(a)
            \left[ x , y \right]
        """
        return x._latex_()

    def _ascii_art_term(self, x):
        r"""
        Return an ascii art representation for ``x``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x,y')
            sage: H = L.Hall()
            sage: x,y = H.gens()
            sage: H._ascii_art_term(x.leading_support())
            x
            sage: a = H([x, y]).leading_support()
            sage: H._ascii_art_term(a)
            [x, y]
        """
        from sage.typeset.ascii_art import ascii_art
        return ascii_art(x)

    def _unicode_art_term(self, x):
        r"""
        Return a unicode art representation for ``x``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x,y')
            sage: H = L.Hall()
            sage: x,y = H.gens()
            sage: H._unicode_art_term(x.leading_support())
            x
            sage: a = H([x, y]).leading_support()
            sage: H._unicode_art_term(a)
            [x, y]
        """
        from sage.typeset.unicode_art import unicode_art
        return unicode_art(x)

    def _element_constructor_(self, x):
        """
        Convert ``x`` into ``self``.

        EXAMPLES::

            sage: L.<x,y> = LieAlgebra(QQ)
            sage: Lyn = L.Lyndon()
            sage: Lyn('x')
            x
            sage: elt = Lyn([x, y]); elt
            [x, y]
            sage: elt.parent() is Lyn
            True
        """
        if not isinstance(x, list) and x in self._indices:
            return self.monomial(x)
        return super()._element_constructor_(x)

    def monomial(self, x):
        """
        Return the monomial indexed by ``x``.

        EXAMPLES::

            sage: Lyn = LieAlgebra(QQ, 'x,y').Lyndon()
            sage: x = Lyn.monomial('x'); x
            x
            sage: x.parent() is Lyn
            True
        """
        if not isinstance(x, (LieGenerator, GradedLieBracket)):
            if isinstance(x, list):
                return super()._element_constructor_(x)
            else:
                i = self._indices.index(x)
                x = LieGenerator(x, i)
        return self.element_class(self, {x: self.base_ring().one()})

    def _construct_UEA(self):
        """
        Construct the universal enveloping algebra of ``self``.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L._construct_UEA()
            Free Algebra on 2 generators (x, y) over Rational Field
            sage: L.<x> = LieAlgebra(QQ)
            sage: L._construct_UEA()
            Free Algebra on 1 generators (x,) over Rational Field
        """
        return FreeAlgebra(self.base_ring(), len(self._names), self._names)

    def is_abelian(self):
        """
        Return ``True`` if this is an abelian Lie algebra.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 3, 'x')
            sage: L.is_abelian()
            False
            sage: L = LieAlgebra(QQ, 1, 'x')
            sage: L.is_abelian()
            True
        """
        return len(self._indices) <= 1

    def basis(self):
        """
        Return the basis of ``self``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 3, 'x')
            sage: L.Hall().basis()
            Disjoint union of Lazy family (graded basis(i))_{i in Positive integers}
        """
        from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
        from sage.sets.positive_integers import PositiveIntegers
        from sage.sets.family import Family
        return DisjointUnionEnumeratedSets(Family(PositiveIntegers(), self.graded_basis, name="graded basis"))

    @cached_method
    def graded_dimension(self, k):
        r"""
        Return the dimension of the ``k``-th graded piece of ``self``.

        The `k`-th graded part of a free Lie algebra on `n` generators
        has dimension

        .. MATH::

            \frac{1}{k} \sum_{d \mid k} \mu(d) n^{k/d},

        where `\mu` is the Mobius function.

        REFERENCES:

        [MKO1998]_

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x', 3)
            sage: H = L.Hall()
            sage: [H.graded_dimension(i) for i in range(1, 11)]
            [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880]
            sage: H.graded_dimension(0)
            0
        """
        if k == 0:
            return 0
        from sage.arith.all import moebius
        s = len(self.lie_algebra_generators())
        k = ZZ(k) # Make sure we have something that is in ZZ
        return sum(moebius(d) * s**(k // d) for d in k.divisors()) // k

    @abstract_method
    def graded_basis(self, k):
        """
        Return the basis for the ``k``-th graded piece of ``self``.

        EXAMPLES::

            sage: H = LieAlgebra(QQ, 3, 'x').Hall()
            sage: H.graded_basis(2)
            ([x0, x1], [x0, x2], [x1, x2])
        """

    @abstract_method
    def _rewrite_bracket(self, l, r):
        """
        Rewrite the bracket ``[l, r]`` in terms of the given basis.

        INPUT:

        - ``l``, ``r`` -- two keys of a basis such that ``l < r``

        OUTPUT:

        A dictionary ``{b: c}`` where ``b`` is a basis key
        and ``c`` is the corresponding coefficient.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 'x,y,z')
            sage: H = L.Hall()
            sage: x,y,z = H.gens()
            sage: H([x, [y, [z, x]]]) # indirect doctest
            -[y, [x, [x, z]]] - [[x, y], [x, z]]
        """

    Element = FreeLieAlgebraElement

class FreeLieAlgebra(Parent, UniqueRepresentation):
    r"""
    The free Lie algebra of a set `X`.

    The free Lie algebra `\mathfrak{g}_X` of a set `X` is the Lie algebra
    with generators `\{g_x\}_{x \in X}` where there are no other relations
    beyond the defining relations. This can be constructed as
    the free magmatic algebra `M_X` quotiented by the ideal
    generated by `\bigl( xx, xy + yx, x(yz) + y(zx) + z(xy) \bigr)`.

    EXAMPLES:

    We first construct the free Lie algebra in the Hall basis::

        sage: L = LieAlgebra(QQ, 'x,y,z')
        sage: H = L.Hall()
        sage: x,y,z = H.gens()
        sage: h_elt = H([x, [y, z]]) + H([x - H([y, x]), H([x, z])]); h_elt
        [x, [x, z]] + [y, [x, z]] - [z, [x, y]] + [[x, y], [x, z]]

    We can also use the Lyndon basis and go between the two::

        sage: Lyn = L.Lyndon()
        sage: l_elt = Lyn([x, [y, z]]) + Lyn([x - Lyn([y, x]), Lyn([x, z])]); l_elt
        [x, [x, z]] + [[x, y], [x, z]] + [x, [y, z]]
        sage: Lyn(h_elt) == l_elt
        True
        sage: H(l_elt) == h_elt
        True

    TESTS:

    Check that we can convert between the two bases::

        sage: L = LieAlgebra(QQ, 'x,y,z')
        sage: Lyn = L.Lyndon()
        sage: H = L.Hall()
        sage: all(Lyn(H(x)) == x for x in Lyn.graded_basis(5))
        True
        sage: all(H(Lyn(x)) == x for x in H.graded_basis(5))
        True
    """
    @staticmethod
    def __classcall_private__(cls, R, names=None, index_set=None):
        """
        Normalize input to ensure a unique representation.

        EXAMPLES::

            sage: from sage.algebras.lie_algebras.free_lie_algebra import FreeLieAlgebra
            sage: L1 = FreeLieAlgebra(QQ, ['x', 'y', 'z'])
            sage: L2.<x,y,z> = LieAlgebra(QQ)
            sage: L1 is L2
            True
        """
        names, index_set = standardize_names_index_set(names, index_set)
        return super().__classcall__(cls, R, names, index_set)

    def __init__(self, R, names, index_set):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: L = LieAlgebra(QQ, 3, 'x')
            sage: TestSuite(L).run()
        """
        self._names = names
        self._indices = index_set
        Parent.__init__(self, base=R, names=names,
                        category=LieAlgebras(R).WithRealizations())

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: LieAlgebra(QQ, 3, 'x')
            Free Lie algebra generated by (x0, x1, x2) over Rational Field
        """
        n = tuple(map(LieGenerator, self._names, range(len(self._names)))) # To remove those stupid quote marks
        return "Free Lie algebra generated by {} over {}".format(n, self.base_ring())

    def _construct_UEA(self):
        """
        Construct the universal enveloping algebra of ``self``.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L._construct_UEA()
            Free Algebra on 2 generators (x, y) over Rational Field
        """
        # TODO: Pass the index set along once FreeAlgebra accepts it
        return FreeAlgebra(self.base_ring(), len(self._names), self._names)

    def lie_algebra_generators(self):
        """
        Return the Lie algebra generators of ``self`` in the Lyndon basis.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.lie_algebra_generators()
            Finite family {'x': x, 'y': y}
            sage: L.lie_algebra_generators()['x'].parent()
            Free Lie algebra generated by (x, y) over Rational Field in the Lyndon basis
        """
        return self.Lyndon().lie_algebra_generators()

    def gens(self):
        """
        Return the generators of ``self`` in the Lyndon basis.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.gens()
            (x, y)
            sage: L.gens()[0].parent()
            Free Lie algebra generated by (x, y) over Rational Field in the Lyndon basis
        """
        return self.Lyndon().gens()

    def gen(self, i):
        """
        Return the ``i``-th generator of ``self`` in the Lyndon basis.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.gen(0)
            x
            sage: L.gen(1)
            y
            sage: L.gen(0).parent()
            Free Lie algebra generated by (x, y) over Rational Field in the Lyndon basis
        """
        return self.gens()[i]

    def a_realization(self):
        r"""
        Return a particular realization of ``self`` (the Lyndon basis).

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: L.a_realization()
            Free Lie algebra generated by (x, y) over Rational Field in the Lyndon basis
        """
        return self.Lyndon()

    class Hall(FreeLieBasis_abstract):
        """
        The free Lie algebra in the Hall basis.

        The basis keys are objects of class
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.LieObject`,
        each of which is either a
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.LieGenerator`
        (in degree `1`) or a
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.GradedLieBracket`
        (in degree `> 1`).
        """
        def __init__(self, lie):
            r"""
            EXAMPLES::

                sage: L = LieAlgebra(QQ, 3, 'x')
                sage: TestSuite(L.Hall()).run()
            """
            experimental_warning(16823, "The Hall basis has not been fully proven correct,"
                                        " but currently no bugs are known")
            FreeLieBasis_abstract.__init__(self, lie, "Hall")

            # Register the coercions
            Lyn = lie.Lyndon()
            Hom_HL = Hom(self, Lyn)
            Hom_LH = Hom(Lyn, self)
            LieAlgebraHomomorphism_im_gens(Hom_HL, Lyn.gens()).register_as_coercion()
            LieAlgebraHomomorphism_im_gens(Hom_LH, self.gens()).register_as_coercion()

        @cached_method
        def _generate_hall_set(self, k):
            """
            Generate the Hall set of grade ``k``.

            OUTPUT:

            A sorted tuple of :class:`GradedLieBracket` elements.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 3, 'x')
                sage: H = L.Hall()
                sage: H._generate_hall_set(3)
                ([x0, [x0, x1]],
                 [x0, [x0, x2]],
                 [x1, [x0, x1]],
                 [x1, [x0, x2]],
                 [x1, [x1, x2]],
                 [x2, [x0, x1]],
                 [x2, [x0, x2]],
                 [x2, [x1, x2]])
            """
            if k <= 0:
                return ()
            if k == 1:
                return tuple(map(LieGenerator, self.variable_names(),
                                 range(len(self.variable_names()))))
            if k == 2:
                basis = self._generate_hall_set(1)
                ret = []
                for i,a in enumerate(basis):
                    for b in basis[i+1:]:
                        ret.append( GradedLieBracket(a, b, 2) )
                return tuple(ret)

            # We don't want to do the middle when we're even, so we add 1 and
            #   take the floor after dividing by 2.
            ret = [GradedLieBracket(a, b, k) for i in range(1, (k+1) // 2)
                   for a in self._generate_hall_set(i)
                   for b in self._generate_hall_set(k-i)
                   if b._left <= a]

            # Special case for when k = 4, we get the pairs [[a, b], [x, y]]
            #    where a,b,x,y are all grade 1 elements. Thus if we take
            #    [a, b] < [x, y], we will always be in the Hall set.
            if k == 4:
                basis = self._generate_hall_set(2)
                for i,a in enumerate(basis):
                    for b in basis[i+1:]:
                        ret.append(GradedLieBracket(a, b, k))
            # Do the middle case when we are even and k > 4
            elif k % 2 == 0:
                basis = self._generate_hall_set(k // 2) # grade >= 2
                for i,a in enumerate(basis):
                    for b in basis[i+1:]:
                        if b._left <= a:
                            ret.append(GradedLieBracket(a, b, k))

            # We sort the returned tuple in order to make computing the higher
            #   graded parts of the Hall set easier.
            return tuple(sorted(ret))

        @cached_method
        def graded_basis(self, k):
            """
            Return the basis for the ``k``-th graded piece of ``self``.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x,y,z')
                sage: H = L.Hall()
                sage: H.graded_basis(2)
                ([x, y], [x, z], [y, z])
                sage: H.graded_basis(4)
                ([x, [x, [x, y]]], [x, [x, [x, z]]],
                 [y, [x, [x, y]]], [y, [x, [x, z]]],
                 [y, [y, [x, y]]], [y, [y, [x, z]]],
                 [y, [y, [y, z]]], [z, [x, [x, y]]],
                 [z, [x, [x, z]]], [z, [y, [x, y]]],
                 [z, [y, [x, z]]], [z, [y, [y, z]]],
                 [z, [z, [x, y]]], [z, [z, [x, z]]],
                 [z, [z, [y, z]]], [[x, y], [x, z]],
                 [[x, y], [y, z]], [[x, z], [y, z]])

            TESTS::

                sage: L = LieAlgebra(QQ, 'x,y,z', 3)
                sage: H = L.Hall()
                sage: [H.graded_dimension(i) for i in range(1, 11)]
                [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880]
                sage: [len(H.graded_basis(i)) for i in range(1, 11)]
                [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880]
            """
            one = self.base_ring().one()
            return tuple([self.element_class(self, {x: one})
                          for x in self._generate_hall_set(k)])

        # We require l < r because it is a requirement and to make the
        #    caching more efficient
        @cached_method
        def _rewrite_bracket(self, l, r):
            """
            Rewrite the bracket ``[l, r]`` in terms of the Hall basis.

            INPUT:

            - ``l``, ``r`` -- two keys of the Hall basis with ``l < r``

            OUTPUT:

            A dictionary ``{b: c}`` where ``b`` is a Hall basis key
            and ``c`` is the corresponding coefficient.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x,y,z')
                sage: H = L.Hall()
                sage: x,y,z = H.gens()
                sage: H([x, [y, [z, x]]]) # indirect doctest
                -[y, [x, [x, z]]] - [[x, y], [x, z]]
            """
            # NOTE: If r is not a graded Lie bracket, then l cannot be a
            #   graded Lie bracket by the order respecting the grading
            if not isinstance(r, GradedLieBracket) or r._left <= l:
                # Compute the grade of the new element
                grade = 0
                # If not a graded Lie bracket, it must be a generator so the grade is 1
                if isinstance(l, GradedLieBracket):
                    grade += l._grade
                else:
                    grade += 1
                if isinstance(r, GradedLieBracket):
                    grade += r._grade
                else:
                    grade += 1
                return {GradedLieBracket(l, r, grade): self.base_ring().one()}

            ret = {}

            # Rewrite [a, [b, c]] = [b, [a, c]] + [[a, b], c] with a < b < c
            # Compute the left summand
            for m, inner_coeff in self._rewrite_bracket(l, r._right).items():
                if r._left == m:
                    continue
                elif r._left < m:
                    x, y = r._left, m
                else: # r._left > m
                    x, y = m, r._left
                    inner_coeff = -inner_coeff
                for b_elt, coeff in self._rewrite_bracket(x, y).items():
                    ret[b_elt] = ret.get(b_elt, 0) + coeff * inner_coeff

            # Compute the right summand
            for m, inner_coeff in self._rewrite_bracket(l, r._left).items():
                if m == r._right:
                    continue
                elif m < r._right:
                    x, y = m, r._right
                else: # m > r._right
                    x, y = r._right, m
                    inner_coeff = -inner_coeff
                for b_elt, coeff in self._rewrite_bracket(x, y).items():
                    ret[b_elt] = ret.get(b_elt, 0) + coeff * inner_coeff

            return ret

    class Lyndon(FreeLieBasis_abstract):
        """
        The free Lie algebra in the Lyndon basis.

        The basis keys are objects of class
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.LieObject`,
        each of which is either a
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.LieGenerator`
        (in degree `1`) or a
        :class:`~sage.algebras.lie_algebras.lie_algebra_element.LyndonBracket`
        (in degree `> 1`).

        TESTS:

        We check that :trac:`27069` is fixed::

            sage: Lzxy = LieAlgebra(QQ, ['z','x','y']).Lyndon()
            sage: z,x,y = Lzxy.gens(); z,x,y
            (z, x, y)
            sage: z.bracket(x)
            [z, x]
            sage: y.bracket(z)
            -[z, y]
        """
        def __init__(self, lie):
            r"""
            EXAMPLES::

                sage: L = LieAlgebra(QQ, 3, 'x')
                sage: TestSuite(L.Lyndon()).run()
            """
            FreeLieBasis_abstract.__init__(self, lie, "Lyndon")

        @cached_method
        def _rewrite_bracket(self, l, r):
            """
            Rewrite the bracket ``[l, r]`` in terms of the Lyndon basis.

            INPUT:

            - ``l``, ``r`` -- two keys of the Lyndon basis such
              that ``l < r``

            OUTPUT:

            A dictionary ``{b: c}`` where ``b`` is a Lyndon basis key
            and ``c`` is the corresponding coefficient.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x,y,z')
                sage: Lyn = L.Lyndon()
                sage: x,y,z = Lyn.gens()
                sage: Lyn([x, [y, [z, x]]]) # indirect doctest
                [x, [[x, z], y]]
            """
            assert l < r, "Order mismatch %s > %s"%(l, r)

            if self._is_basis_element(l, r):
                # Compute the grade of the new element
                grade = 0
                # If not a graded Lie bracket, it must be a generator so the grade is 1
                if isinstance(l, GradedLieBracket):
                    grade += l._grade
                else:
                    grade += 1
                if isinstance(r, GradedLieBracket):
                    grade += r._grade
                else:
                    grade += 1
                return {LyndonBracket(l, r, grade): self.base_ring().one()}

            ret = {}

            # Rewrite [[a, b], c] = [a, [b, c]] + [[a, c], b] with a < b < c
            # with a = l._left, b = l._right and c = r.
            # Here, we use the fact that deg(l) > 1, because
            # if we had deg(l) == 1, then the
            # "if self._is_basis_element(l, r)" would already have
            # caught us.
            # For a similar reason, we have b >= c.
            # Compute the left summand
            for m, inner_coeff in self._rewrite_bracket(l._right, r).items():
                if l._left == m:
                    continue
                elif l._left < m:
                    x, y = l._left, m
                else: # l._left > m
                    x, y = m, l._left
                    inner_coeff = -inner_coeff
                for b_elt, coeff in self._rewrite_bracket(x, y).items():
                    ret[b_elt] = ret.get(b_elt, 0) + coeff * inner_coeff

            # Compute the right summand
            for m, inner_coeff in self._rewrite_bracket(l._left, r).items():
                if m == l._right:
                    continue
                elif m < l._right:
                    x, y = m, l._right
                else: # m > l._right
                    x, y = l._right, m
                    inner_coeff = -inner_coeff
                for b_elt, coeff in self._rewrite_bracket(x, y).items():
                    ret[b_elt] = ret.get(b_elt, 0) + coeff * inner_coeff

            return ret

        def _is_basis_element(self, l, r):
            """
            Check if the element ``[l, r]`` formed from
            two basis keys ``l`` and ``r`` is a basis key.

            EXAMPLES::

                sage: Lyn = LieAlgebra(QQ, 'x,y,z').Lyndon()
                sage: all(Lyn._is_basis_element(*x.list()[0][0]) for x in Lyn.graded_basis(4))
                True
            """
            w = tuple(l._index_word + r._index_word)
            if not is_lyndon(w):
                return False
            b = self._standard_bracket(w)
            return b._left == l and b._right == r

        @cached_method
        def _standard_bracket(self, lw):
            """
            Return the standard bracketing (a :class:`LieObject`)
            of a Lyndon word ``lw`` using the Lie bracket.

            INPUT:

            - ``lw`` -- tuple of positive integers that correspond to
              the indices of the generators

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x', 3)
                sage: Lyn = L.Lyndon()
                sage: Lyn._standard_bracket((0, 0, 1))
                [x0, [x0, x1]]
                sage: Lyn._standard_bracket((0, 1, 1))
                [[x0, x1], x1]
            """
            if len(lw) == 1:
                i = lw[0]
                return LieGenerator(self._indices[i], i)

            for i in range(1, len(lw)):
                if is_lyndon(lw[i:]):
                    return LyndonBracket(self._standard_bracket(lw[:i]),
                                         self._standard_bracket(lw[i:]),
                                         len(lw))

        @cached_method
        def graded_basis(self, k):
            """
            Return the basis for the ``k``-th graded piece of ``self``.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x', 3)
                sage: Lyn = L.Lyndon()
                sage: Lyn.graded_basis(1)
                (x0, x1, x2)
                sage: Lyn.graded_basis(2)
                ([x0, x1], [x0, x2], [x1, x2])
                sage: Lyn.graded_basis(4)
                ([x0, [x0, [x0, x1]]],
                 [x0, [x0, [x0, x2]]],
                 [x0, [[x0, x1], x1]],
                 [x0, [x0, [x1, x2]]],
                 [x0, [[x0, x2], x1]],
                 [x0, [[x0, x2], x2]],
                 [[x0, x1], [x0, x2]],
                 [[[x0, x1], x1], x1],
                 [x0, [x1, [x1, x2]]],
                 [[x0, [x1, x2]], x1],
                 [x0, [[x1, x2], x2]],
                 [[[x0, x2], x1], x1],
                 [[x0, x2], [x1, x2]],
                 [[[x0, x2], x2], x1],
                 [[[x0, x2], x2], x2],
                 [x1, [x1, [x1, x2]]],
                 [x1, [[x1, x2], x2]],
                 [[[x1, x2], x2], x2])

            TESTS::

                sage: L = LieAlgebra(QQ, 'x,y,z', 3)
                sage: Lyn = L.Lyndon()
                sage: [Lyn.graded_dimension(i) for i in range(1, 11)]
                [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880]
                sage: [len(Lyn.graded_basis(i)) for i in range(1, 11)]
                [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880]
            """
            if k <= 0 or not self._indices:
                return []

            names = self.variable_names()
            one = self.base_ring().one()
            if k == 1:
                return tuple(self.element_class(self, {LieGenerator(n, k): one})
                             for k,n in enumerate(names))

            from sage.combinat.combinat_cython import lyndon_word_iterator
            n = len(self._indices)
            ret = []
            for lw in lyndon_word_iterator(n, k):
                b = self._standard_bracket(tuple(lw))
                ret.append(self.element_class(self, {b: one}))
            return tuple(ret)

        def pbw_basis(self, **kwds):
            """
            Return the Poincare-Birkhoff-Witt basis corresponding to ``self``.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x,y,z', 3)
                sage: Lyn = L.Lyndon()
                sage: Lyn.pbw_basis()
                The Poincare-Birkhoff-Witt basis of Free Algebra on 3 generators (x, y, z) over Rational Field
            """
            return self.universal_enveloping_algebra().pbw_basis()

        poincare_birkhoff_witt_basis = pbw_basis

#######################################
## Category for the realizations

class FreeLieAlgebraBases(Category_realization_of_parent):
    r"""
    The category of bases of a free Lie algebra.
    """
    def __init__(self, base):
        r"""
        Initialize the bases of a free Lie algebra.

        INPUT:

        - ``base`` -- a free Lie algebra

        TESTS::

            sage: from sage.algebras.lie_algebras.free_lie_algebra import FreeLieAlgebraBases
            sage: L.<x, y> = LieAlgebra(QQ)
            sage: bases = FreeLieAlgebraBases(L)
            sage: L.Hall() in bases
            True
        """
        Category_realization_of_parent.__init__(self, base)

    def _repr_(self):
        r"""
        Return the representation of ``self``.

        EXAMPLES::

            sage: from sage.algebras.lie_algebras.free_lie_algebra import FreeLieAlgebraBases
            sage: L.<x, y> = LieAlgebra(QQ)
            sage: FreeLieAlgebraBases(L)
            Category of bases of Free Lie algebra generated by (x, y) over Rational Field
        """
        return "Category of bases of %s" % self.base()

    def super_categories(self):
        r"""
        The super categories of ``self``.

        EXAMPLES::

            sage: from sage.algebras.lie_algebras.free_lie_algebra import FreeLieAlgebraBases
            sage: L.<x, y> = LieAlgebra(QQ)
            sage: bases = FreeLieAlgebraBases(L)
            sage: bases.super_categories()
            [Category of lie algebras with basis over Rational Field,
             Category of realizations of Free Lie algebra generated by (x, y) over Rational Field]
        """
        return [LieAlgebras(self.base().base_ring()).WithBasis(), Realizations(self.base())]

def is_lyndon(w):
    """
    Modified form of ``Word(w).is_lyndon()`` which uses the default order
    (this will either be the natural integer order or lex order) and assumes
    the input ``w`` behaves like a nonempty list.
    This function here is designed for speed.

    EXAMPLES::

        sage: from sage.algebras.lie_algebras.free_lie_algebra import is_lyndon
        sage: is_lyndon([1])
        True
        sage: is_lyndon([1,3,1])
        False
        sage: is_lyndon((2,2,3))
        True
        sage: all(is_lyndon(x) for x in LyndonWords(3, 5))
        True
        sage: all(is_lyndon(x) for x in LyndonWords(6, 4))
        True
    """
    i = 0
    for let in w[1:]:
        if w[i] < let:
            i = 0
        elif w[i] == let:
            i += 1
        else:
            # we found the first word in the Lyndon factorization.
            return False
    return i == 0
