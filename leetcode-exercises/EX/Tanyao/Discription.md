Ichihime is playing mahjong and she is now doing a All Simple practice. She takes out three ordered arrays, representing the Man tiles, the Sou tiles, and the Pin tiles. The length of each array is 14; the possible values of each element are 0 and 2~8; the sum of the non-zero elements of the three arrays is always 14. The draw for All Simple is as follows: you need **four chows** (e.g. 234, 345, all in the same array) or **pungs** (e.g. 333, 555, all in the same array), plus **two** of the same tiles as the **head** (66, 88, all in the same array). Can you help her calculate whether the deck can be drawn? If not, what is the minimum number of tiles that need to be replaced to make a draw?

**Example 1:**

**Input:** board = [[2,4,5,6,7,8,0,0,0,0,0,0,0,0],[2,3,4,4,5,6,0,0,0,0,0,0,0,0],[5,5,0,0,0,0,0,0,0,0,0,0,0,0]]
**Output:** false, 1
**Explanation:**** Replace the 2 in the first group with a 3 to form the pattern.

**Example 2:**

**Input:** board = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,3,3,3,4,4,4,6,6,6,8,8],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
**Output:** true, 0
**Explanation:** Contains three sets of chows, one set of pung, and a head.

**Constraints:**

- `board.length == 3`
- `board[i].length == 14`
- The possible values of each element are `0` and `2~8`.
