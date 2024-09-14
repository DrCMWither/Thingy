/**
 * To dealing with these, we have to find out roles each terms play. If you know Lambda in Java,
 * then you should handle it more quickly then I think.
 * 
 * Take 3 types o a term:
 * 
 * e.g.
 * VAR   LAM   APP
 * @Lx.  @Ly.  x
 * 
 * 
 * Just one night for this little shit, who cares about it
 * @author Dr. Lilia Chen May Wither
 * @since  0.1
 * @see    <a href="https://en.wikipedia.org/wiki/Lambda_calculus">Lambda calculus</a>
 */


import java.util.Stack;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class LambdaCalculus {

  enum TermType {
       VAR,
       LAM,
       APP
    }

  private TermType type;
  private Object data;

  public Term(TermType type, Object data) {
    this.type = type;
    this.data = data;
    return this;
  }

  /*
  public TermType getType() {
    return type;
  }

  public Object getData() {
    return data;
  }
   */

  public class Term {
    TermType type;
    int varIndex;
    Term lamTerm;
    Term argTerm;

  /**
   * @param type     The type of the term (VAR, LAM, or APP).
   * @param varIndex The index of the variable (for VAR only).
   * @param lamTerm  The body term of the lambda abstraction (for LAM only).
   * @param argTerm  The left operand term of the application (for APP only).
   */
    public Term(TermType type, int varIndex, Term lamTerm, Term argTerm) {
      this.type = type;
      this.varIndex = varIndex;
      this.lamTerm = lamTerm;
      this.argTerm = argTerm;
    }
  }

  /**
   * @param index The index of the variable (0-based).
   * @return      A new Term object with type TermType.VAR and the specified index.
   */
  static Term createVarTerm(int index) {
    return new Term(TermType.VAR, index, null, null);
  }

  /**
   * @param innerTerm The term that forms the body of the lambda abstraction.
   * @return          A new Term object with type TermType.LAM and the provided innerTerm.
   */
  static Term createLamTerm(Term innerTerm) {
    return new Term(TermType.LAM, 0, innerTerm, null);
  }

  /**
   * @param left  The left operand term.
   * @param right The right operand term.
   * @return      A new Term object with type TermType.APP, the left and the right term.
   */
  static Term createAppTerm(Term left, Term right) {
    return new Term(TermType.APP, 0, left, right);
  }

  /**
   * @param term                  The term to be printed.
   * @throws NullPointerException if the provided term is null.
   */
  static void printTerm(Term term) {

    
    if (term == null) {
      return;
    }

    switch (term.type) {
      case VAR:
        System.out.print("x" + term.varIndex);
        break;
      case LAM:
        System.out.print("(lambda ");
        printTerm(term.lamTerm);
        System.out.print(")");
        break;
      case APP:
        System.out.print("(");
        printTerm(term.argTerm);
        System.out.print(" ");
        printTerm(term.argTerm);
        System.out.print(")");
        break;
      }
    }
  }

  /**
   * @param str The string representation of the lambda term.
   * @return    The parsed Term object, or null if there's a parsing error.
   */
  static Term parseTerm(String str) {
    Stack<Term> stack = new Stack<>();
    for (char c : str.toCharArray()) {
      switch (c) {
        case '(':
          break;
        case ')': {
          Term term2 = stack.pop();
          if (stack.isEmpty()) {
            return term2;
          }
          Term term1 = stack.pop();
          stack.push(createAppTerm(term1, term2));
          break;
        }
        case '\\': {
          if (stack.isEmpty()) {
            throw new IllegalArgumentException("Error: Lambda without argument");
            return null;
          }
          Term innerTerm = stack.pop();
          stack.push(createLamTerm(innerTerm));
          break;
        }
        default:
          if (Character.isAlphabetic(c)) {
            int varIndex = c - 'x';
            stack.push(createVarTerm(varIndex));
          } else {
            throw new IllegalArgumentException("Error: Unexpected character at: " + c);
            return null;
          }
      }
    }
    throw new IllegalArgumentException("Error: Unmatched parenthesis");
    return null;
  }
  
  /**
   * @param term                      The term to be converted.
   * @param boundVarIndex             boundVarIndex The index of the variable to be renamed (bound variable).
   * @param freshVarIndex             freshVarIndex The index to be used for the new variable (fresh variable).
   * @return                          A new term object with the alpha conversion applied, or null if the original term is null.
   * @throws IllegalArgumentException if the term type is unknown.
   * 
   * @see                             https://en.wikipedia.org/wiki/Lambda_calculus#%CE%B1-conversion
   */
  static Term convertTerm(Term term, int boundVarIndex, int freshVarIndex) {
    if (term == null) {
      return null;
    }

    switch (term.type) {
      case VAR:
        if (term.varIndex == boundVarIndex) {
          return createVarTerm(freshVarIndex);
        } else {
          return createVarTerm(term.varIndex);
        }
      case LAM:
        return createLamTerm(convertTerm(term.lamTerm, boundVarIndex, freshVarIndex));
      case APP:
        return createAppTerm(convertTerm(term.argTerm, boundVarIndex, freshVarIndex),
               convertTerm(term.argTerm, boundVarIndex, freshVarIndex));
      default:
        throw new IllegalArgumentException("Unknown term type");
    }
  }

  /**
   * @param term The term to be evaluated.
   * @return     The evaluated term after applying beta-reduction (if applicable), 
   *             or null if evaluation fails.
   * 
   * @see        https://en.wikipedia.org/wiki/Lambda_calculus#%CE%B2-reduction_2
   */
  static Term evaluateTerm(Term term) {
    if (term == null) {
      return null;
    }
    if (term.type == TermType.VAR) {
      return term;
    } else if (term.type == TermType.LAM) {
      return term;
    } else if (term.type == TermType.APP) {
      Term left = evaluateTerm(term.argTerm);
      Term right = evaluateTerm(term.argTerm);
      if (left.type == TermType.LAM) {
        Term newBody = substitute(left.lamTerm, 0, right);
        return createLamTerm(newBody);
      } else {
        return createAppTerm(left, right);
      }
    }
    return null;
  }


  /**
   * @param term      The term to search for variable indices.
   * @param usedIndex The index of a variable that is considered used (to be avoided).
   * @return          The smallest fresh variable index found within the term, or 0, if there's no variables exist.
   */
  static int findFreshVarIndex(Term term, int usedIndex) {
    if (term == null) {
      return 0;
    }

    switch (term.type) {
      case TermType.VAR:
        if (term.varIndex == usedIndex) {
          return findFreshVarIndex(term.lamTerm, usedIndex + 1) + 1;
        } else {
          return Math.max(findFreshVarIndex(term.lamTerm, usedIndex), term.varIndex + 1);
        }
      case TermType.LAM:
        return findFreshVarIndex(term.lamTerm, usedIndex);
      case TermType.APP:
        int leftIndex = findFreshVarIndex(term.argTerm, usedIndex);
        int rightIndex = findFreshVarIndex(term.argTerm, usedIndex);
        return Math.max(leftIndex, rightIndex);
    }
  }

  /**
   * @param term     The term on which to perform substitution.
   * @param varIndex The index of the variable to be replaced.
   * @param argTerm  The term to be used as the replacement.
   * @return         A new Term object with the substitutions applied;
   *                 Returns null if the original term is null.
   */
  static Term substitute(Term term, int varIndex, Term argTerm) {
    if (term == null) {
      return null;
    }

    Term newTerm = new Term(term.type, term.varIndex, null, null);

    switch (term.type) {
      case VAR:
        if (term.varIndex == varIndex) {
          newTerm.type = argTerm.type;
          if (argTerm.type == TermType.VAR) {
            newTerm.varIndex = argTerm.varIndex;
          } else {
            newTerm.lamTerm = convertTerm(argTerm.lamTerm, varIndex, term.varIndex);
            newTerm.argTerm = convertTerm(argTerm.argTerm, varIndex, term.varIndex);
          }
        } else {
          newTerm.varIndex = term.varIndex;
        }
          break;
      case LAM:
        int freshIndex = findFreshVarIndex(term, varIndex);
        newTerm.lamTerm = substitute(term.lamTerm, varIndex, createVarTerm(freshIndex));
        break;
      case APP:
        newTerm.argTerm = substitute(term.argTerm, varIndex, argTerm);
        newTerm.argTerm = substitute(term.argTerm, varIndex, argTerm);
        break;
        default:
          throw new IllegalArgumentException("Unknown term type");
    }
  return newTerm;
}



/**
 * @param x The x-coordinate of the point.
 * @param y The y-coordinate of the point. 
 */
class Point {
  int x;
  int y;

  public Point(int x, int y) {
    this.x = x;
    this.y = y;
  }
}

/**
 * @param width  The width of the dimension.
 * @param height The height of the dimension.
 */ 
class Dimension {
  int width;
  int height;

  public Dimension(int width, int height) {
    this.width = width;
    this.height = height;
  }
}

/**
 * @param term                      The lambda term for which to calculate the bounding box.
 * @return                          A {@link Dimension} object representing the width and height of the bounding box.
 * @throws IllegalArgumentException if the term has an unknown type.
 */
class TermDrawer {

  public Dimension getTermBoundingBox(Term term) {
    if (term == null) {
      return new Dimension(0, 0);
    }
    switch (term.getType()) {
      case VAR:
        return new Dimension(2, 1);
      case LAM:
        Dimension innerDim = getTermBoundingBox(term.getLamTerm());
        return new Dimension(innerDim.getWidth() + 8, Math.max(2, innerDim.getHeight() + 1));
      case APP:
        Dimension leftDim = getTermBoundingBox(term.getArgTerm());
        Dimension rightDim = getTermBoundingBox(term.getRightArgTerm());
        return new Dimension(leftDim.getWidth() + rightDim.getWidth() + 2,
                   Math.max(leftDim.getHeight(), rightDim.getHeight()) + 1);
      default:
        throw new IllegalArgumentException("Unknown term type");
    }
  }

  /**
   * @param os The {@link PrintStream} where the drawing instructions are written.
   * @param p1 The starting point of the line segment.
   * @param p2 The ending point of the line segment.
   */
  public void drawLine(PrintStream os, Point p1, Point p2) {
    os.println("drawLine " + p1.getX() + " " + p1.getY() + " " + p2.getX() + " " + p2.getY());
  }

  public void drawLineV(PrintStream os, Point p1, Point p2) {
    os.println("drawLineV " + p1.getX() + " " + p1.getY() + " " + p2.getX() + " " + p2.getY());
  }

  /**
   * @param os   The {@link PrintStream} where the drawing instructions are written.
   * @param text The text to be drawn.
   * @param p    The position where the text should be drawn.
   */
  public void drawText(PrintStream os, String text, Point p) {
    os.println("drawText " + p.getX() + " " + p.getY() + " " + text);
  }
}

/**
 * @param os                        The PrintStream to which the drawing instructions will be written.
 * @param term                      The lambda term to be drawn.
 * @param origin                    The starting Point (top-left corner) for the drawing.
 * @throws IllegalArgumentException if the term has an unknown type.
 */
public void drawTerm(PrintStream os, Term term, Point origin) {
    if (term == null) {
        return;
    }

    Dimension dim = getTermBoundingBox(term);
    switch (term.getType()) {
      case VAR:
        drawText(os, "x" + term.getVarIndex(), origin);
        break;
      case LAM:
        drawText(os, "(lambda ", origin);
        Point innerOrigin = new Point(origin.getX() + 4, origin.getY());
        drawTerm(os, term.getLamTerm(), innerOrigin);
        drawText(os, ")", new Point(origin.getX() + dim.getWidth() - 4, origin.getY()));
        drawLine(os, new Point(origin.getX() + 2, origin.getY()), new Point(origin.getX() + 2, origin.getY() + dim.getHeight()));
        break;
      case APP:
        Point leftOrigin = origin;
        Point rightOrigin = new Point(origin.getX() + getTermBoundingBox(term.getArgTerm()).getWidth() + 1, origin.getY());
        drawTerm(os, term.getArgTerm(), leftOrigin);
        drawTerm(os, term.getArgTerm(), rightOrigin);
        drawLineV(os, new Point(leftOrigin.getX() + dim.getWidth() / 2, origin.getY() + 1),
                      new Point(leftOrigin.getX() + dim.getWidth() / 2, origin.getY() + dim.getHeight()));
        break;
      default:
        throw new IllegalArgumentException("Unknown term type");
  }
}

  /**
   * @param term                      The lambda term to be animated.
   * @param frameNum                  The frame number (used for animation positioning).
   * @return                          A String representation of the animation frame.
   * @throws IllegalArgumentException if the provided term is null.
   */
public class LambdaTermAnimation {

  public static String generateAnimationFrame(Term term, int frameNum) {
    ByteArrayOutputStream frameStream = new ByteArrayOutputStream();
    PrintStream os = new PrintStream(frameStream);
    new TermDrawer().drawTerm(os, term, new Point(frameNum * 50, 20));
    return new String(frameStream.toByteArray());
  }

  public static List<String> generateAnimationFrames(Term term) {
    List<String> frames = new ArrayList<>();
    for (int i = 0; i < 10; ++i) {
      frames.add(generateAnimationFrame(term, i));
    }
    return frames;
  }
}
  
/**
 * @param args shit.
 */
public static void main(String[] args) {
  Scanner scanner = new Scanner(System.in);
  System.out.print("Enter a lambda calculus term: ");
  String termStr = scanner.nextLine();
  Term term = parseTerm(termStr);

  if (term == null) {
    System.out.println("Error: Invalid term." + System.lineSeparator());
    return;
  }

  System.out.println("Original term: ");
  printTerm(term);
  System.out.println();

  Term evaluatedTerm = evaluateTerm(term);

  if (evaluatedTerm != null) {
    System.out.println("Generating animation for evaluated term..." + System.lineSeparator());
    List<String> frames = generateAnimationFrames(evaluatedTerm);

    for (String frame : frames) {
      System.out.println(frame);
      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
        System.out.println("Evaluated term: ");
    printTerm(evaluatedTerm);
    System.out.println();
  } else {
    System.out.println("Error: Evaluation failed." + System.lineSeparator());
  }
}